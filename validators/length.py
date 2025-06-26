"""字符串长度验证器

验证字符串字段的长度是否在指定范围内。
"""

from typing import Dict, Any, Tuple


def validate_field(field_name: str, value: Any, params: Dict[str, Any], row_data: Dict[str, Any]) -> Tuple[bool, str]:
    """字符串长度验证
    
    验证字符串字段的长度在指定的最小和最大长度范围内。
    
    参数：
    - min: 最小长度（可选）
    - max: 最大长度（可选）
    
    示例配置：
    { field = "Name", script = "length.py", params = { min = 1, max = 50 } }
    { field = "Description", script = "length.py", params = { min = 10, max = 200 } }
    { field = "Code", script = "length.py", params = { min = 3 } }
    """
    
    str_value = str(value) if value is not None else ""
    length = len(str_value)
    
    min_length = params.get('min')
    max_length = params.get('max')
    
    if min_length is not None and length < min_length:
        return False, f"Field '{field_name}' length {length} is less than minimum {min_length}"
    
    if max_length is not None and length > max_length:
        return False, f"Field '{field_name}' length {length} is greater than maximum {max_length}"
    
    return True, ""