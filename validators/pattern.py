"""正则表达式验证器

使用正则表达式验证字段值的格式。
"""

from typing import Dict, Any, Tuple
import re


def validate_field(field_name: str, value: Any, params: Dict[str, Any], row_data: Dict[str, Any]) -> Tuple[bool, str]:
    """正则表达式验证
    
    使用正则表达式验证字段值是否符合指定的格式。
    
    参数：
    - pattern: 正则表达式模式（必需）
    
    示例配置：
    { field = "Email", script = "pattern.py", params = { pattern = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$" } }
    { field = "Phone", script = "pattern.py", params = { pattern = "^\\d{3}-\\d{4}-\\d{4}$" } }
    { field = "Icon", script = "pattern.py", params = { pattern = "^[a-zA-Z0-9_]+\\.(png|jpg|jpeg|gif)$" } }
    """
    
    pattern = params.get('pattern')
    if not pattern:
        return False, f"Pattern validation for field '{field_name}' requires 'pattern' parameter"
    
    str_value = str(value) if value is not None else ""
    
    try:
        if re.match(pattern, str_value):
            return True, ""
        else:
            return False, f"Field '{field_name}' value '{str_value}' does not match pattern '{pattern}'"
    except re.error as e:
        return False, f"Invalid regular expression pattern '{pattern}': {e}"