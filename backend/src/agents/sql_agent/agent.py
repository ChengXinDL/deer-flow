import logging
from typing import Any

from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware, TodoListMiddleware
from langchain_core.runnables import RunnableConfig
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit

from src.agents.sql_agent.prompt import apply_prompt_template
from src.agents.middlewares.clarification_middleware import ClarificationMiddleware
from src.agents.middlewares.dangling_tool_call_middleware import DanglingToolCallMiddleware
from src.agents.middlewares.memory_middleware import MemoryMiddleware
from src.agents.middlewares.thread_data_middleware import ThreadDataMiddleware
from src.agents.middlewares.uploads_middleware import UploadsMiddleware
from src.agents.thread_state import ThreadState
from src.config.app_config import get_app_config
from src.config.summarization_config import get_summarization_config
from src.models import create_chat_model
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def _resolve_model_name(requested_model_name: str | None) -> str:
    """Resolve a runtime model name safely, falling back to default if invalid. Returns None if no models are configured."""
    app_config = get_app_config()
    default_model_name = app_config.models[0].name if app_config.models else None
    if default_model_name is None:
        raise ValueError(
            "No chat models are configured. Please configure at least one model in config.yaml."
        )

    if requested_model_name and app_config.get_model_config(requested_model_name):
        return requested_model_name

    if requested_model_name and requested_model_name != default_model_name:
        logger.warning(f"Model '{requested_model_name}' not found in config; fallback to default model '{default_model_name}'.")
    return default_model_name


def _create_summarization_middleware() -> SummarizationMiddleware | None:
    """Create and configure the summarization middleware from config."""
    config = get_summarization_config()

    if not config.enabled:
        return None

    # Prepare trigger parameter
    trigger = None
    if config.trigger is not None:
        if isinstance(config.trigger, list):
            trigger = [t.to_tuple() for t in config.trigger]
        else:
            trigger = config.trigger.to_tuple()

    # Prepare keep parameter
    keep = config.keep.to_tuple()

    # Prepare model parameter
    if config.model_name:
        model = config.model_name
    else:
        # Use a lightweight model for summarization to save costs
        # Falls back to default model if not explicitly specified
        model = create_chat_model(thinking_enabled=False)

    # Prepare kwargs
    kwargs = {
        "model": model,
        "trigger": trigger,
        "keep": keep,
    }

    if config.trim_tokens_to_summarize is not None:
        kwargs["trim_tokens_to_summarize"] = config.trim_tokens_to_summarize

    if config.summary_prompt is not None:
        kwargs["summary_prompt"] = config.summary_prompt

    return SummarizationMiddleware(**kwargs)


def _create_todo_list_middleware(is_plan_mode: bool) -> TodoListMiddleware | None:
    """Create and configure the TodoList middleware.

    Args:
        is_plan_mode: Whether to enable plan mode with TodoList middleware.

    Returns:
        TodoListMiddleware instance if plan mode is enabled, None otherwise.
    """
    if not is_plan_mode:
        return None

    # Custom prompts matching magicflow's style
    system_prompt = """
<todo_list_system>
You have access to the `write_todos` tool to help you manage and track complex multi-step objectives.

**CRITICAL RULES:**
- Mark todos as completed IMMEDIATELY after finishing each step - do NOT batch completions
- Keep EXACTLY ONE task as `in_progress` at any time (unless tasks can run in parallel)
- Update the todo list in REAL-TIME as you work - this gives users visibility into your progress
- DO NOT use this tool for simple tasks (< 3 steps) - just complete them directly

**When to Use:**
This tool is designed for complex objectives that require systematic tracking:
- Complex multi-step tasks requiring 3+ distinct steps
- Non-trivial tasks needing careful planning and execution
- User explicitly requests a todo list
- User provides multiple tasks (numbered or comma-separated list)
- The plan may need revisions based on intermediate results

**When NOT to Use:**
- Single, straightforward tasks
- Trivial tasks (< 3 steps)
- Purely conversational or informational requests
- Simple tool calls where the approach is obvious

**Best Practices:**
- Break down complex tasks into smaller, actionable steps
- Use clear, descriptive task names
- Remove tasks that become irrelevant
- Add new tasks discovered during implementation
- Don't be afraid to revise the todo list as you learn more

**Task Management:**
Writing todos takes time and tokens - use it when helpful for managing complex problems, not for simple requests.
</todo_list_system>
"""

    tool_description = """Use this tool to create and manage a structured task list for complex work sessions.

**IMPORTANT: Only use this tool for complex tasks (3+ steps). For simple requests, just do the work directly.**

## When to Use

Use this tool in these scenarios:
1. **Complex multi-step tasks**: When a task requires 3 or more distinct steps or actions
2. **Non-trivial tasks**: Tasks requiring careful planning or multiple operations
3. **User explicitly requests todo list**: When the user directly asks you to track tasks
4. **Multiple tasks**: When users provide a list of things to be done
5. **Dynamic planning**: When the plan may need updates based on intermediate results

## When NOT to Use

Skip this tool when:
1. The task is straightforward and takes less than 3 steps
2. The task is trivial and tracking provides no benefit
3. The task is purely conversational or informational
4. It's clear what needs to be done and you can just do it

## How to Use

1. **Starting a task**: Mark it as `in_progress` BEFORE beginning work
2. **Completing a task**: Mark it as `completed` IMMEDIATELY after finishing
3. **Updating the list**: Add new tasks, remove irrelevant ones, or update descriptions as needed
4. **Multiple updates**: You can make several updates at once (e.g., complete one task and start the next)

## Task States

- `pending`: Task not yet started
- `in_progress`: Currently working on (can have multiple if tasks run in parallel)
- `completed`: Task finished successfully

## Task Completion Requirements

**CRITICAL: Only mark a task as completed when you have FULLY accomplished it.**

Never mark a task as completed if:
- There are unresolved issues or errors
- Work is partial or incomplete
- You encountered blockers preventing completion
- You couldn't find necessary resources or dependencies
- Quality standards haven't been met

If blocked, keep the task as `in_progress` and create a new task describing what needs to be resolved.

## Best Practices

- Create specific, actionable items
- Break complex tasks into smaller, manageable steps
- Use clear, descriptive task names
- Update task status in real-time as you work
- Mark tasks complete IMMEDIATELY after finishing (don't batch completions)
- Remove tasks that are no longer relevant
- **IMPORTANT**: When you write the todo list, mark your first task(s) as `in_progress` immediately
- **IMPORTANT**: Unless all tasks are completed, always have at least one task `in_progress` to show progress

Being proactive with task management demonstrates thoroughness and ensures all requirements are completed successfully.

**Remember**: If you only need a few tool calls to complete a task and it's clear what to do, it's better to just do the task directly and NOT use this tool at all.
"""

    return TodoListMiddleware(system_prompt=system_prompt, tool_description=tool_description)


# ThreadDataMiddleware must be before other middleware to ensure thread_id is available
# UploadsMiddleware should be after ThreadDataMiddleware to access thread_id
# DanglingToolCallMiddleware patches missing ToolMessages before model sees the history
# SummarizationMiddleware should be early to reduce context before other processing
# TodoListMiddleware should be before ClarificationMiddleware to allow todo management
# MemoryMiddleware queues conversation for memory update
# ClarificationMiddleware should be last to intercept clarification requests after model calls
def _build_middlewares(config: RunnableConfig):
    """Build middleware chain based on runtime configuration.

    Args:
        config: Runtime configuration containing configurable options like is_plan_mode.

    Returns:
        List of middleware instances.
    """
    middlewares = [ThreadDataMiddleware(), UploadsMiddleware(), DanglingToolCallMiddleware()]

    # Add summarization middleware if enabled
    summarization_middleware = _create_summarization_middleware()
    if summarization_middleware is not None:
        middlewares.append(summarization_middleware)

    # Add TodoList middleware if plan mode is enabled
    is_plan_mode = config.get("configurable", {}).get("is_plan_mode", False)
    todo_list_middleware = _create_todo_list_middleware(is_plan_mode)
    if todo_list_middleware is not None:
        middlewares.append(todo_list_middleware)

    # Add MemoryMiddleware
    middlewares.append(MemoryMiddleware())

    # ClarificationMiddleware should always be last
    middlewares.append(ClarificationMiddleware())
    return middlewares


def _get_sql_tools(db: SQLDatabase, model) -> list:
    """Get SQL tools from database toolkit.

    Args:
        db: SQL database connection.
        model: Language model for toolkit initialization.

    Returns:
        List of SQL tools.
    """
    toolkit = SQLDatabaseToolkit(db=db, llm=model)
    sql_tools = toolkit.get_tools()
    
    from src.tools.builtins.elements_show_tool import (
        command_show_elements,
        command_color_elements,
        command_save_file,
    )
    
    bim_tools = [
        command_show_elements,
        command_color_elements,
        command_save_file,
    ]
    
    return sql_tools + bim_tools


def make_sql_agent(config: RunnableConfig):
    """Create a SQL query agent for BIM model databases.

    Args:
        config: Runtime configuration containing:
            - db_url: Database connection URL
            - building_id: Building ID to query
            - model_name: Model name to use
            - thinking_enabled: Whether to enable thinking mode
            - is_plan_mode: Whether to enable plan mode

    Returns:
        Configured SQL agent instance.
    """
    # Extract configuration
    db_url = config.get("configurable", {}).get("db_url")
    building_id = config.get("configurable", {}).get("building_id")
    requested_model_name = config.get("configurable", {}).get("model_name") or config.get("configurable", {}).get("model")
    thinking_enabled = config.get("configurable", {}).get("thinking_enabled", True)
    reasoning_effort = config.get("configurable", {}).get("reasoning_effort", None)
    is_plan_mode = config.get("configurable", {}).get("is_plan_mode", False)

    # Validate required parameters
    if not db_url:
        db_url = "mysql+mysqlconnector://app:sykj_1234A@192.168.8.221:3307/bim_data"
    if not building_id:
        building_id = "335834679343"

    # Resolve model name
    model_name = _resolve_model_name(requested_model_name)
    if model_name is None:
        raise ValueError(
            "No chat model could be resolved. Please configure at least one model in "
            "config.yaml or provide a valid 'model_name'/'model' in the request."
        )

    app_config = get_app_config()
    model_config = app_config.get_model_config(model_name) if model_name else None
    if thinking_enabled and model_config is not None and not model_config.supports_thinking:
        logger.warning(f"Thinking mode is enabled but model '{model_name}' does not support it; fallback to non-thinking mode.")
        thinking_enabled = False

    logger.info(
        "thinking_enabled: %s, reasoning_effort: %s, model_name: %s, is_plan_mode: %s, building_id: %s",
        thinking_enabled,
        reasoning_effort,
        model_name,
        is_plan_mode,
        building_id,
    )

    # Connect to database - use lazy reflection to avoid loading all schema at once
    # This prevents context overflow when database has many tables
    db = SQLDatabase.from_uri(
        db_url,
        sample_rows_in_table_info=0,
        lazy_table_reflection=True,
    )

    # Create model and get SQL tools
    model = create_chat_model(name=model_name, thinking_enabled=thinking_enabled, reasoning_effort=reasoning_effort)
    tools = _get_sql_tools(db, model)

    # Print available SQL tools
    print("=" * 60)
    print("【可用的SQL工具列表】")
    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool.name}: {tool.description}")
    print("=" * 60)

    # Inject run metadata for LangSmith trace tagging
    if "metadata" not in config:
        config["metadata"] = {}
    config["metadata"].update(
        {
            "model_name": model_name or "default",
            "thinking_enabled": thinking_enabled,
            "reasoning_effort": reasoning_effort,
            "is_plan_mode": is_plan_mode,
            "building_id": building_id,
        }
    )

    # Build agent kwargs
    agent_kwargs: dict[str, Any] = {
        "model": model,
        "tools": tools,
        "middleware": _build_middlewares(config),
        "system_prompt": apply_prompt_template(building_id=building_id),
        "state_schema": ThreadState,
    }
    
    # Add checkpointer if provided in config
    checkpointer = config.get("configurable", {}).get("checkpointer")
    if checkpointer is not None:
        agent_kwargs["checkpointer"] = checkpointer
    
    return create_agent(**agent_kwargs)
