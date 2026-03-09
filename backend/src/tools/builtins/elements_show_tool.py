from typing import Annotated, Literal, Optional
import json
import re
import random
from collections import defaultdict

import pandas as pd

from langchain.tools import InjectedToolCallId, ToolRuntime, tool
from langgraph.types import Command
from langgraph.typing import ContextT

from src.agents.thread_state import ThreadState

import logging

logger = logging.getLogger(__name__)


@tool("show_elements", parse_docstring=True)
def command_show_elements(
    runtime: ToolRuntime[ContextT, ThreadState],
    function: Literal["seperateElement", "hideElement", "showLevel", "seperateRoom"],
    element_ids: list[str],
    building_id: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Separate or hide elements in the BIM model.

    When to use this tool:
    - When you need to isolate specific elements for viewing
    - When you need to hide elements to focus on specific areas
    - When you need to show specific levels or rooms

    When NOT to use this tool:
    - For coloring elements (use color_elements instead)
    - For saving views (use save_view instead)
    - For non-BIM operations

    Args:
        function: Operation type. Options: 'seperateElement', 'hideElement', 'showLevel', 'seperateRoom'
        element_ids: List of element global IDs to operate on
        building_id: Building model ID
    """
    try:
        # 构建标准化结构
        element_dict = {
            "function": function,
            "parameters": {
                "element_ids": element_ids,
                "model_id": building_id
            }
        }
        return Command(
            update={"messages": [{
                "type": "tool_message",
                "content": f"Successfully executed {function} on {len(element_ids)} elements",
                "tool_call_id": tool_call_id
            }]},
            command=element_dict
        )
    except Exception as e:
        error_message = f"Error executing {function}: {str(e)}"
        logger.error(error_message)
        return Command(
            update={"messages": [{
                "type": "tool_message",
                "content": error_message,
                "tool_call_id": tool_call_id
            }]},
            command={"function": function, "error": str(e)}
        )

@tool("color_elements", parse_docstring=True)
def command_color_elements(
    runtime: ToolRuntime[ContextT, ThreadState],
    function: Literal["brushColor", "resetColor", "brushModelColor"],
    tool_call_id: Annotated[str, InjectedToolCallId],
    element_ids: Optional[list[str]] = None,
    color: Optional[tuple[float, float, float, float]] = None,
    building_id: Optional[str] = None,
) -> Command:
    """Color elements in the BIM model.

    When to use this tool:
    - When you need to color specific elements
    - When you need to reset colors
    - When you need to set the base color for the entire model

    When NOT to use this tool:
    - For separating or hiding elements (use show_elements instead)
    - For saving views (use save_view instead)
    - For non-BIM operations

    Args:
        function: Operation type. Options: 'brushColor', 'resetColor', 'brushModelColor'
        element_ids: List of element global IDs to color (required for brushColor)
        color: RGBA color tuple (r, g, b, a) where values are 0-255 for RGB and 0-1 for alpha
        building_id: Building model ID (required for brushColor)
    """
    try:
        # 构建 parameters 字典，仅包含非 None 的参数
        parameters = {}
        if element_ids is not None:
            parameters["element_ids"] = element_ids
        if color is not None:
            parameters["color"] = color
        if building_id is not None:
            parameters["model_id"] = building_id
        
        # 构建命令字典
        command_dict = {"function": function}
        if parameters:  # 只有当 parameters 非空时才添加
            command_dict["parameters"] = parameters
        
        # 构建成功消息
        if function == "resetColor":
            message = "Successfully reset all colors"
        elif function == "brushModelColor":
            message = "Successfully set model base color"
        else:
            message = f"Successfully colored {len(element_ids)} elements"
        
        return Command(
            update={"messages": [{
                "type": "tool_message",
                "content": message,
                "tool_call_id": tool_call_id
            }]},
            command=command_dict
        )
    except Exception as e:
        error_message = f"Error executing {function}: {str(e)}"
        logger.error(error_message)
        return Command(
            update={"messages": [{
                "type": "tool_message",
                "content": error_message,
                "tool_call_id": tool_call_id
            }]},
            command={"function": function, "error": str(e)}
        )

@tool("save_view", parse_docstring=True)
def command_save_file(
    runtime: ToolRuntime[ContextT, ThreadState],
    function: Literal["snapShot"],
    filepath: str,
    description: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Save a snapshot of the current view.

    When to use this tool:
    - When you need to save the current view as an image
    - When you need to document a specific state of the model
    - When you want to share a view with others

    When NOT to use this tool:
    - For coloring elements (use color_elements instead)
    - For separating or hiding elements (use show_elements instead)
    - For non-BIM operations

    Args:
        function: Must be 'snapShot'
        filepath: Path where the snapshot should be saved
        description: Description of the snapshot
    """
    try:
        # 构建标准化输出
        command_dict = {
            "function": function,
            "parameters": {
                "path": filepath,
                "description": description
            }
        }
        return Command(
            update={"messages": [{
                "type": "tool_message",
                "content": f"Successfully saved snapshot to {filepath}",
                "tool_call_id": tool_call_id
            }]},
            command=command_dict
        )
    except Exception as e:
        error_message = f"Error saving snapshot: {str(e)}"
        logger.error(error_message)
        return Command(
            update={"messages": [{
                "type": "tool_message",
                "content": error_message,
                "tool_call_id": tool_call_id
            }]},
            command={"function": function, "error": str(e)}
        )

class Color:
    """Color class for handling RGB/RGBA colors."""
    
    def __init__(self, r: int, g: int, b: int, a: float = 0.7):
        """Initialize Color object with RGB values (0-255).
        
        Args:
            r (int): Red component (0-255)
            g (int): Green component (0-255)
            b (int): Blue component (0-255)
            a (float): Alpha (transparency) component (0.0-1.0), default 0.7
        """
        # Clamp values to valid ranges
        self.r = max(0, min(255, r))
        self.g = max(0, min(255, g))
        self.b = max(0, min(255, b))
        self.a = max(0.0, min(1.0, float(a)))
    
    def to_hex(self) -> str:
        """Convert color to hex string format (e.g., #FF5733)."""
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}"
    
    def to_hexa(self) -> str:
        """Convert color to hex string with alpha channel (e.g., #FF5733D9)."""
        alpha_hex = f"{int(self.a * 255):02X}"
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}{alpha_hex}"
    
    def to_rgb(self) -> tuple:
        """Return RGB tuple (r, g, b)."""
        return (self.r, self.g, self.b)
    
    def to_rgba(self) -> tuple:
        """Return RGBA tuple (r, g, b, a)."""
        return (self.r, self.g, self.b, self.a)
    
    def to_rgba_str(self) -> str:
        """Return space-separated RGBA string format."""
        return f"{self.r} {self.g} {self.b} {self.a}"
    
    def with_alpha(self, new_alpha: float):
        """Return a new Color object with modified alpha value."""
        return Color(self.r, self.g, self.b, new_alpha)
    
    def __repr__(self):
        """Return string representation of the Color object."""
        if abs(self.a - 0.7) < 1e-6:  # Default alpha, can omit
            return f"Color(r={self.r}, g={self.g}, b={self.b})"
        else:
            return f"Color(r={self.r}, g={self.g}, b={self.b}, a={self.a})"
        
    def __str__(self):
        """Return RGBA string format for direct output."""
        return self.to_rgba_str()
    
    def __eq__(self, other):
        """Implement equality comparison."""
        if isinstance(other, Color):
            return (
                self.r == other.r and 
                self.g == other.g and 
                self.b == other.b and 
                abs(self.a - other.a) < 1e-6
            )
        return False


def generate_distinct_colors(count: int) -> list[Color]:
    """Generate visually distinct colors using predefined RGB values.

    Args:
        count (int): Number of distinct colors needed

    Returns:
        list[Color]: List of Color objects with distinct colors
    """
    if count == 0:
        return []

    # Predefined RGB colors that are visually distinct
    base_colors = [
        (255, 0, 0),  # Red
        (0, 255, 0),  # Green
        (0, 0, 255),  # Blue
        (255, 255, 0),  # Yellow
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Cyan
        (255, 128, 0),  # Orange
        (128, 0, 255),  # Purple
        (255, 128, 128),  # Pink
        (128, 255, 128),  # Light Green
        (128, 128, 255),  # Light Blue
        (255, 255, 128),  # Light Yellow
        (128, 0, 0),  # Dark Red
        (0, 128, 0),  # Dark Green
        (0, 0, 128),  # Dark Blue
        (128, 128, 0),  # Olive
        (128, 0, 128),  # Dark Magenta
        (0, 128, 128),  # Teal
        (192, 192, 192),  # Silver
        (128, 128, 128),  # Gray
        (255, 192, 203),  # Light Pink
        (255, 165, 0),  # Orange Red
        (255, 20, 147),  # Deep Pink
        (50, 205, 50),  # Lime Green
        (30, 144, 255),  # Dodger Blue
    ]

    colors = []
    for i in range(count):
        if i < len(base_colors):
            # Use predefined colors
            r, g, b = base_colors[i]
        else:
            # Generate additional colors by cycling and modifying
            base_idx = i % len(base_colors)
            cycle = i // len(base_colors)
            r, g, b = base_colors[base_idx]

            # Modify brightness to create variations
            factor = 1.0 - (cycle * 0.15)  # Reduce brightness by 15% each cycle
            factor = max(0.3, factor)  # Don't go too dark

            r = int(r * factor)
            g = int(g * factor)
            b = int(b * factor)

        color = Color(r, g, b)
        colors.append(color)

    return colors


def generate_gradient_colors(count: int) -> list[Color]:
    """Generate gradient colors from blue to red with better distribution.

    Args:
        count (int): Number of gradient colors needed

    Returns:
        list[Color]: List of Color objects representing the gradient
    """
    if count <= 1:
        return [Color(255, 0, 0)]

    colors = []
    for i in range(count):
        # Create more distinct gradient from blue to red
        ratio = float(i) / (count - 1)

        # Use HSV color space for better distribution
        red = int(255 * ratio)
        green = int(255 * (1 - abs(2 * ratio - 1)))  # Peak at middle
        blue = int(255 * (1 - ratio))

        colors.append(Color(red, green, blue))

    return colors


def interpolate_color(position: float) -> Color:
    """Interpolate color based on position (0.0 to 1.0) for smooth gradients.

    Args:
        position (float): Position in gradient (0.0 to 1.0)

    Returns:
        Color: Interpolated color
    """
    # Clamp position to valid range
    position = max(0.0, min(1.0, position))

    # Blue to Red gradient with green in middle
    red = int(255 * position)
    green = int(255 * (1 - abs(2 * position - 1)))  # Peak at middle
    blue = int(255 * (1 - position))

    return Color(red, green, blue)

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color string to RGB tuple.

    Args:
        hex_color (str): Hex color string (e.g., "#FF0000" or "FF0000")

    Returns:
        tuple[int, int, int]: RGB tuple (r, g, b)
    """
    # Remove # if present
    hex_color = hex_color.lstrip("#")

    # Convert to RGB
    try:
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    except (ValueError, IndexError):
        logger.error("Invalid hex color: %s. Using red as fallback.", hex_color)
        return (255, 0, 0)

def safe_color_to_hex(color) -> str:
    """Safely convert color object to hex string.

    Args:
        color: Color object with Red, Green, Blue properties

    Returns:
        str: Hex color string
    """
    try:
        r = max(0, min(255, int(color.Red)))
        g = max(0, min(255, int(color.Green)))
        b = max(0, min(255, int(color.Blue)))
        return "#{:02x}{:02x}{:02x}".format(r, g, b)
    except Exception:
        return "#FF0000"

def generate_random_color() -> tuple[int, int, int]:
    """Generate a random RGB color.

    Returns:
        tuple[int, int, int]: RGB tuple (r, g, b)
    """
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def color_elements_by_parameter(
    analized_result: list, 
    parameter_name: str | list, 
    use_gradient: bool = False, 
    custom_colors: list | None = None
) -> dict:
    """Color elements in a model based on parameter values with proper gradient support.

    Args:
        analized_result (list): List of analyzed results to color
        parameter_name (str | list): Name of the parameter to use for coloring
        use_gradient (bool): Whether to use gradient coloring
        custom_colors (list): Optional list of custom hex colors

    Returns:
        dict: Results of the coloring operation
    """

    if not analized_result:
        return {
            "status": "warning",
            "message": "analized_result not found"
        }
    
    # 检查表头是否包含必要的标识列
    headers = analized_result[0]
    REQUIRED_COLUMNS = ["Space_model_id", "所在楼层", "空间名称", "floor_model_id"]

    if isinstance(parameter_name, list):
        parameter_name = parameter_name[0]

    available_id_columns = [col for col in REQUIRED_COLUMNS if col in headers]
    if not available_id_columns:
        logger.warning(f"表头缺少必要的元素标识列，需包含至少一个：{REQUIRED_COLUMNS}")
        return {
            "status": "warning",
            "message": f"表头缺少元素标识列，需包含以下至少一个：{', '.join(REQUIRED_COLUMNS)}"
        }
    
    try:
        # 选择优先级最高的标识列（第一个存在的列）
        selected_id_column = available_id_columns[0]
        logger.debug(f"选择元素标识列：{selected_id_column}（可用标识列：{available_id_columns}）")

        # 创建DataFrame并校验参数列存在性
        df = pd.DataFrame.from_records(analized_result[1:], columns=headers)

        # Group elements by parameter value
        parameter_groups = defaultdict(list)
        value_data = {}  # Store both raw and display values

        # 检查参数列是否存在
        if parameter_name in list(df.columns) and selected_id_column in list(df.columns):
            # 确保参数列是字符串类型
            df[parameter_name] = df[parameter_name].astype(str)

            # 按参数分组，将标识列值收集到列表中
            parameter_groups = df.groupby(parameter_name)[selected_id_column].apply(list).sort_index(ascending=False).to_dict()
            # 尝试将参数值转换为整数（用于数值梯度）
            for k in parameter_groups:
                try:
                    value_data[k] = int(k)
                except ValueError:
                    value_data[k] = k
            
            logger.debug(f"parameter_groups: {parameter_groups}")
            logger.debug(f"value_data: {value_data}")
        
        logger.debug(f"dataframe[:2]: {df.iloc[:2]}")

        if parameter_name not in list(df.columns):
            available_cols = list(df.columns)
            logger.debug({
                "status": "error",
                "message": f"参数 '{parameter_name}' 不在数据列中。可用列: {available_cols}"
            })
            return {
                "status": "error",
                "message": f"参数 '{parameter_name}' 不在数据列中。可用列: {available_cols}"
            }
        
        # Check for numeric gradient mode
        is_numeric_gradient = use_gradient and any(
            param_name in parameter_name
            for param_name in [
                "数量",
                "floor_model_id"
            ]
        )
        
        logger.debug(f"is_numeric_gradient: {is_numeric_gradient}")

        if is_numeric_gradient:
            # For numeric parameters in gradient mode, treat each unique value individually
            # but still group elements with identical values
            unique_values = df[parameter_name].unique().tolist()
            value_count = len(unique_values)

            # Create mapping from value to position in gradient
            value_positions = {}
            numeric_values = []

            for display_value in unique_values:
                raw_value = value_data.get(display_value, display_value)
                if isinstance(raw_value, (int, float)):
                    numeric_values.append(raw_value)

            if numeric_values:
                min_val = min(numeric_values)
                max_val = max(numeric_values)

                for display_value in unique_values:
                    raw_value = value_data.get(display_value, display_value)
                    if isinstance(raw_value, (int, float)) and max_val != min_val:
                        position = (raw_value - min_val) / (max_val - min_val)
                        value_positions[display_value] = position
                    else:
                        value_positions[display_value] = 0.5
            else:
                # Fallback if no numeric values
                for i, display_value in enumerate(unique_values):
                    value_positions[display_value] = float(i) / max(
                        1, len(unique_values) - 1
                    )
        else:
            unique_values = df[parameter_name].unique().tolist()
            value_count = len(unique_values)

        logger.debug(f"value_positions: {value_positions}")
        logger.debug(f"unique_values: {unique_values}")
        
        # Generate colors based on the sorted order
        if custom_colors:
            # Use custom colors
            colors = []
            for i, hex_color in enumerate(custom_colors):
                if i >= value_count:
                    break
                rgb = hex_to_rgb(hex_color)
                colors.append(Color(rgb[0], rgb[1], rgb[2]))

            # Fill remaining with distinct colors if needed
            if len(colors) < value_count:
                remaining_count = value_count - len(colors)
                additional_colors = generate_distinct_colors(remaining_count)
                colors.extend(additional_colors)

        elif use_gradient and is_numeric_gradient:
            # Use interpolated colors for numeric gradients
            colors = []
            for param_value in unique_values:
                position = value_positions.get(param_value, 0.5)
                color = interpolate_color(position)
                colors.append(color)
        elif use_gradient:
            # Generate proper gradient colors for non-numeric
            colors = generate_gradient_colors(value_count)
        else:
            # Use distinct colors
            colors = generate_distinct_colors(value_count)
        logger.debug(colors)

        # Apply colors to elements
        color_assignments = {}

        for i, param_value in enumerate(unique_values):
            if param_value not in parameter_groups:
                continue
                
            group_elements = parameter_groups[param_value]

            # Get color for this group
            if i < len(colors):
                color = colors[i]
            else:
                logger.warning(
                    "Color index out of bounds for value %s at index %d",
                    param_value,
                    i,
                )
                rgb = generate_random_color()
                color = Color(rgb[0], rgb[1], rgb[2])

            color_assignments[param_value] = {
                "color": color.with_alpha(0.98).to_rgba(),
                "element_ids": group_elements,
                "sort_index": i,  # Add sort index for debugging
            }

        return color_assignments

    except Exception as e:
        logger.error("Error in color_elements_by_parameter: %s", e)
        return {
            "status": "error",
            "message": f"Failed to color elements: {str(e)}",
        }
    
def commands_formated_output(commands_list: list) -> str:
    """Format commands list into a human-readable string.

    Args:
        commands_list (list): List of command dictionaries

    Returns:
        str: Formatted commands string
    """
    txt_commands = ""
    try:
        for command in commands_list:
            operate = command.get('function')
            
            parameter = command.get('parameters', {})
            element_ids = parameter.get('element_ids')

            if operate == 'snapShot':
                filepath = parameter.get('path')
                description = parameter.get('description', '')
                if filepath:
                    txt_commands += f"{operate} {filepath} {description}\n"
                continue

            elif operate == 'resetColor':
                txt_commands += f"{operate}\n"
                continue

            if not element_ids:
                continue

            element_ids_str = ', '.join(element_ids)
            if operate == 'seperateElement':       
                if element_ids_str:
                    txt_commands += f"{operate} {element_ids_str}\n"
                
            elif operate == 'brushColor':
                color = parameter.get('color')
                if color and isinstance(color, (tuple, list)):
                    color_str = ', '.join(str(val) for val in color)
                    txt_commands += f"{operate} {element_ids_str} {color_str}\n"
    except Exception as e:
        logger.error("Error formatting commands: %s", e)
        return f"Error: Failed to convert commands to string. {str(e)}"

    return txt_commands

def commands_show_and_save_colored_view(
    analized_result: list, 
    parameter_name: str | list, 
    building_id: str, 
    filepath: str, 
    description: str
) -> list:
    """Generate commands to color elements and save the view.

    Args:
        analized_result (list): List of analyzed results
        parameter_name (str | list): Parameter name to color by
        building_id (str): Building model ID
        filepath (str): Path to save the snapshot
        description (str): Description of the snapshot

    Returns:
        list: List of commands
    """
    logger.debug(f"analized_result:\n{analized_result}")
    id_with_color_dict = color_elements_by_parameter(analized_result, parameter_name, use_gradient=True, custom_colors=None)
    
    # Check if color assignment was successful
    if "status" in id_with_color_dict and id_with_color_dict["status"] != "success":
        logger.warning(f"Color assignment failed: {id_with_color_dict.get('message', 'Unknown error')}")
        return []
    
    commands = []
    collected_element_ids = []
    base_color = Color(127, 127, 127, 0.05).to_rgba()
    
    # Set base model color
    base_color_command = command_color_elements("brushModelColor", color=base_color)
    commands.append(base_color_command)
    
    # Color elements by parameter
    for key, val in id_with_color_dict.items():
        assigned_color = val.get('color')
        # 累积所有的element_ids
        assigned_element_ids = val.get('element_ids', [])
        collected_element_ids.extend(assigned_element_ids)
        # 给每一批element_ids 添加颜色
        if assigned_element_ids and assigned_color:
            color_command = command_color_elements("brushColor", assigned_element_ids, assigned_color, building_id)
            commands.append(color_command)

    # Save the colored view
    save_color_view_command = command_save_file("snapShot", filepath, description)
    commands.append(save_color_view_command)

    logger.debug(f"commands:\n{commands}")

    return commands


@tool("query_level_ids", parse_docstring=True)
def query_level_ids_by_name(
    runtime: ToolRuntime[ContextT, ThreadState],
    input: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Get level IDs by name.

    When to use this tool:
    - When you need to get level IDs for specific floor names
    - When you need to show specific levels in the BIM model

    Args:
        input: JSON string with building_id and floor_names
    """
    try:
        # 确保input是字符串类型
        if not isinstance(input, str):
            return Command(
                update={"messages": [{"type": "tool_message", "content": "Error: input must be a string.", "tool_call_id": tool_call_id}]},
                command={"error": "input must be a string"}
            )
        
        input_data = json.loads(input)
        building_id = input_data.get("building_id")
        floor_names = input_data.get("floor_names", [])

        logger.debug(f"query_level_ids_by_name: building_id={building_id}, floor_names={floor_names}")
        
        if not building_id:
            return Command(
                update={"messages": [{"type": "tool_message", "content": "Error: Building ID is required.", "tool_call_id": tool_call_id}]},
                command={"error": "Building ID is required"}
            )
        
        if not isinstance(floor_names, list):
            return Command(
                update={"messages": [{"type": "tool_message", "content": "Error: floor_names must be a list.", "tool_call_id": tool_call_id}]},
                command={"error": "floor_names must be a list"}
            )
        
        if len(floor_names) == 0:
            return Command(
                update={"messages": [{"type": "tool_message", "content": "No floor names provided.", "tool_call_id": tool_call_id}]},
                command={"function": "showLevel", "parameters": {"element_ids": [], "model_id": building_id}}
            )
        
        # Note: Database connection should be obtained from configuration
        # For now, return a mock response
        # In production, you would execute the actual query
        mock_level_ids = [f"level_{i}" for i in range(len(floor_names))]
        
        # 返回结果
        return command_show_elements(runtime, "showLevel", mock_level_ids, building_id, tool_call_id)
        
    except json.JSONDecoMAGICror as e:
        error_message = f"Error: Invalid JSON input. {str(e)}"
        logger.error(error_message)
        return Command(
            update={"messages": [{"type": "tool_message", "content": error_message, "tool_call_id": tool_call_id}]},
            command={"error": error_message}
        )
    except Exception as e:
        error_message = f"Error: {str(e)}"
        logger.error(error_message)
        return Command(
            update={"messages": [{"type": "tool_message", "content": error_message, "tool_call_id": tool_call_id}]},
            command={"error": error_message}
        )


@tool("query_room_ids", parse_docstring=True)
def query_room_ids_by_name(
    runtime: ToolRuntime[ContextT, ThreadState],
    input: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Get room IDs by name.

    When to use this tool:
    - When you need to get room IDs for specific room names
    - When you need to separate specific rooms in the BIM model

    Args:
        input: JSON string with building_id and room_names
    """
    try:
        input_data = json.loads(input)
        building_id = input_data.get("building_id")
        room_names = input_data.get("room_names", [])

        logger.debug(f"query_room_ids_by_name: building_id={building_id}, room_names={room_names}")

        # 验证参数
        if not building_id:
            return Command(
                update={"messages": [{"type": "tool_message", "content": "Error: Building ID is required.", "tool_call_id": tool_call_id}]},
                command={"error": "Building ID is required"}
            )
        
        if not isinstance(room_names, list) or not all(isinstance(name, str) for name in room_names):
            return Command(
                update={"messages": [{"type": "tool_message", "content": "Error: Room names must be a list of strings.", "tool_call_id": tool_call_id}]},
                command={"error": "Room names must be a list of strings"}
            )
        
        if not room_names:
            return Command(
                update={"messages": [{"type": "tool_message", "content": "No room names provided.", "tool_call_id": tool_call_id}]},
                command={"function": "seperateRoom", "parameters": {"element_ids": [], "model_id": building_id}}
            )
        
        # 使用正则表达式去掉 "Rm " 前缀
        cleaned_names = [re.sub(r'^Rm\s*', '', name) for name in room_names]
        logger.debug(f"Cleaned room names: {cleaned_names}")
        
        # Note: Database connection should be obtained from configuration
        # For now, return a mock response
        mock_room_ids = [f"room_{i}" for i in range(len(cleaned_names))]
        
        # 返回结果
        return command_show_elements(runtime, "seperateRoom", mock_room_ids, building_id, tool_call_id)
        
    except json.JSONDecoMAGICror as e:
        error_message = f"Error: Invalid JSON input. {str(e)}"
        logger.error(error_message)
        return Command(
            update={"messages": [{"type": "tool_message", "content": error_message, "tool_call_id": tool_call_id}]},
            command={"error": error_message}
        )
    except Exception as e:
        error_message = f"Error: {str(e)}"
        logger.error(error_message)
        return Command(
            update={"messages": [{"type": "tool_message", "content": error_message, "tool_call_id": tool_call_id}]},
            command={"error": error_message}
        )


@tool("separate_element", parse_docstring=True)
def seperate_element_by_guid(
    runtime: ToolRuntime[ContextT, ThreadState],
    input: str | dict,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Separate elements by their GUIDs in the current view.

    When to use this tool:
    - When you need to isolate specific elements for viewing
    - When you need to focus on particular elements in the BIM model

    Args:
        input: JSON string or dict with building_id and element_guid
    """
    try:
        if isinstance(input, str):
            input_data = json.loads(input)
        else:
            input_data = input
        
        building_id = input_data.get("building_id")
        element_guids = input_data.get("element_guid", [])

        logger.debug(f"seperate_element_by_guid: building_id={building_id}, element_guids={element_guids}")

        # 验证参数
        if not building_id:
            return Command(
                update={"messages": [{"type": "tool_message", "content": "Error: Building ID is required.", "tool_call_id": tool_call_id}]},
                command={"error": "Building ID is required"}
            )
        
        if not isinstance(element_guids, list) or not all(isinstance(guid, str) for guid in element_guids):
            return Command(
                update={"messages": [{"type": "tool_message", "content": "Error: element_guid must be a list of strings.", "tool_call_id": tool_call_id}]},
                command={"error": "element_guid must be a list of strings"}
            )
        
        if not element_guids:
            return Command(
                update={"messages": [{"type": "tool_message", "content": "No element GUIDs provided.", "tool_call_id": tool_call_id}]},
                command={"function": "seperateElement", "parameters": {"element_ids": [], "model_id": building_id}}
            )
        
        # Note: Database connection should be obtained from configuration
        # For now, return a mock response
        mock_element_ids = [f"element_{i}" for i in range(len(element_guids))]
        
        # 返回结果
        return command_show_elements(runtime, "seperateElement", mock_element_ids, building_id, tool_call_id)
        
    except json.JSONDecoMAGICror as e:
        error_message = f"Error: Invalid JSON input. {str(e)}"
        logger.error(error_message)
        return Command(
            update={"messages": [{"type": "tool_message", "content": error_message, "tool_call_id": tool_call_id}]},
            command={"error": error_message}
        )
    except Exception as e:
        error_message = f"Error: {str(e)}"
        logger.error(error_message)
        return Command(
            update={"messages": [{"type": "tool_message", "content": error_message, "tool_call_id": tool_call_id}]},
            command={"error": error_message}
        )


@tool("query_all_elements", parse_docstring=True)
def query_all_element_ids(
    runtime: ToolRuntime[ContextT, ThreadState],
    input: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Get all element IDs for given GUIDs and room names.

    When to use this tool:
    - When you need to get multiple element IDs at once
    - When you need to separate multiple elements in the BIM model

    Args:
        input: JSON string with building_id, element_guid, and room_names
    """
    try:
        input_data = json.loads(input)
        building_id = input_data.get("building_id")
        element_guids = input_data.get("element_guid", [])
        room_names = input_data.get("room_names", [])

        logger.debug(f"query_all_element_ids: building_id={building_id}, element_guids={element_guids}, room_names={room_names}")

        # 验证参数
        if not building_id:
            return Command(
                update={"messages": [{"type": "tool_message", "content": "Error: Building ID is required.", "tool_call_id": tool_call_id}]},
                command={"error": "Building ID is required"}
            )
        
        if not isinstance(room_names, list) or not all(isinstance(name, str) for name in room_names):
            return Command(
                update={"messages": [{"type": "tool_message", "content": "Error: room names must be a list of strings.", "tool_call_id": tool_call_id}]},
                command={"error": "room names must be a list of strings"}
            )
        
        if not element_guids and not room_names:
            return Command(
                update={"messages": [{"type": "tool_message", "content": "No element GUIDs or room names provided.", "tool_call_id": tool_call_id}]},
                command={"function": "seperateElement", "parameters": {"element_ids": [], "model_id": building_id}}
            )
        
        # 使用正则表达式去掉 "Rm " 前缀
        cleaned_names = [re.sub(r'^Rm\s*', '', name) for name in room_names]
        logger.debug(f"Cleaned room names: {cleaned_names}")
        
        # Note: Database connection should be obtained from configuration
        # For now, return a mock response
        mock_element_ids = []
        if element_guids:
            mock_element_ids.extend([f"element_{i}" for i in range(len(element_guids))])
        if cleaned_names:
            mock_element_ids.extend([f"room_{i}" for i in range(len(cleaned_names))])
        
        # 返回结果
        return command_show_elements(runtime, "seperateElement", mock_element_ids, building_id, tool_call_id)
        
    except json.JSONDecoMAGICror as e:
        error_message = f"Error: Invalid JSON input. {str(e)}"
        logger.error(error_message)
        return Command(
            update={"messages": [{"type": "tool_message", "content": error_message, "tool_call_id": tool_call_id}]},
            command={"error": error_message}
        )
    except Exception as e:
        error_message = f"Error: {str(e)}"
        logger.error(error_message)
        return Command(
            update={"messages": [{"type": "tool_message", "content": error_message, "tool_call_id": tool_call_id}]},
            command={"error": error_message}
        )


__all__ = [
    "command_show_elements",
    "command_color_elements",
    "command_save_file",
    "Color",
    "generate_distinct_colors",
    "generate_gradient_colors",
    "interpolate_color",
    "hex_to_rgb",
    "safe_color_to_hex",
    "generate_random_color",
    "color_elements_by_parameter",
    "commands_formated_output",
    "commands_show_and_save_colored_view",
    "query_level_ids_by_name",
    "query_room_ids_by_name",
    "seperate_element_by_guid",
    "query_all_element_ids",
]


