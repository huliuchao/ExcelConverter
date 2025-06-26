"""必填验证器

验证字段是否为必填项。
"""

from typing import Dict, Any, Tuple


def validate_field(field_name: str, value: Any, params: Dict[str, Any], row_data: Dict[str, Any]) -> Tuple[bool, str]:
    """必填验证
    
    验证字段不能为空（None或空字符串）。
    
    参数：
    - 无需额外参数
    
    示例配置：
    { field = "AchievementID", script = "required.py" }
    """
    
    if value is None or str(value).strip() == "":
        return False, f"Field '{field_name}' is required but empty"
    
    return True, ""