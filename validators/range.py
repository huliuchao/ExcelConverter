"""数值范围验证器

验证数值字段是否在指定范围内。
"""

from typing import Dict, Any, Tuple


def validate_field(field_name: str, value: Any, params: Dict[str, Any], row_data: Dict[str, Any]) -> Tuple[bool, str]:
    """数值范围验证
    
    验证数值字段在指定的最小值和最大值范围内。
    
    参数：
    - min: 最小值（可选）
    - max: 最大值（可选）
    
    示例配置：
    { field = "Level", script = "range.py", params = { min = 1, max = 100 } }
    { field = "Price", script = "range.py", params = { min = 0 } }
    { field = "Percentage", script = "range.py", params = { max = 100 } }
    """
    
    try:
        num_value = float(value) if value is not None else 0
    except (ValueError, TypeError):
        return False, f"Field '{field_name}' value '{value}' is not a number"
    
    min_val = params.get('min')
    max_val = params.get('max')
    
    if min_val is not None and num_value < min_val:
        return False, f"Field '{field_name}' value {num_value} is less than minimum {min_val}"
    
    if max_val is not None and num_value > max_val:
        return False, f"Field '{field_name}' value {num_value} is greater than maximum {max_val}"
    
    return True, ""