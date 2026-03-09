"""Read file tool for accessing skill documents and other files."""

from pathlib import Path

from langchain.tools import ToolRuntime, tool
from langchain_core.messages import ToolMessage
from langgraph.typing import ContextT

from src.agents.thread_state import ThreadState
from src.sandbox.tools import get_thread_data, replace_virtual_path


@tool("read_file", parse_docstring=True)
def read_file_tool(
    file_path: str,
    runtime: ToolRuntime[ContextT, ThreadState] | None = None,
    tool_call_id: str | None = None,
) -> dict:
    """Read the contents of a file.

    Use this tool to read skill documents, reference files, or any text file.
    This is essential for the skill system to work properly.

    When to use the read_file tool:
    - Reading skill documentation (SKILL.md files)
    - Reading reference documents and examples
    - Reading configuration files
    - Any time you need to access file contents for processing

    Args:
        file_path: Absolute path to the file to read. For skill files, use the path
                  provided in the skill's <location> tag.

    Returns:
        A dictionary with file contents or error message.
    """
    try:
        # Get thread data for path replacement
        thread_data = get_thread_data(runtime)

        # Replace virtual paths if needed
        actual_path = replace_virtual_path(file_path, thread_data)

        path = Path(actual_path)

        # Validate that the file exists
        if not path.exists():
            return {
                "messages": [ToolMessage(f"Error: File not found: {file_path}", tool_call_id=tool_call_id)]
            }

        # Validate that it's a file (not a directory)
        if not path.is_file():
            return {
                "messages": [ToolMessage(f"Error: Path is not a file: {file_path}", tool_call_id=tool_call_id)]
            }

        # Read file contents
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return {
                "messages": [ToolMessage(content, tool_call_id=tool_call_id)]
            }
        except UnicodeDecodeError:
            # Try with different encoding
            with open(path, "r", encoding="gbk") as f:
                content = f.read()
            return {
                "messages": [ToolMessage(content, tool_call_id=tool_call_id)]
            }

    except Exception as e:
        return {
            "messages": [ToolMessage(f"Error reading file: {str(e)}", tool_call_id=tool_call_id)]
        }
