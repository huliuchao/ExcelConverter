"""枚举值验证器

验证字段值是否在允许的枚举值列表中。
"""

from typing import Dict, Any, Tuple


def validate_field(field_name: str, value: Any, params: Dict[str, Any], row_data: Dict[str, Any]) -> Tuple[bool, str]:
    """枚举值验证
    
    验证字段值必须在预定义的允许值列表中。
    
    参数：
    - values: 允许的值列表（必需）
    
    示例配置：
    { field = "AchievementType", script = "enum.py", params = { values = ["daily", "main", "achievement", "event"] } }
    """
    
    allowed_values = params.get('values', [])
    
    if not allowed_values:
        return False, f"Enum validation for field '{field_name}' requires 'values' parameter"
    
    if value in allowed_values:
        return True, ""
    else:
        return False, f"Field '{field_name}' value '{value}' not in allowed values: {allowed_values}"