"""数组长度验证器

验证数组字段的元素数量是否在指定范围内。
"""

from typing import Dict, Any, Tuple, List


def validate_field(field_name: str, value: Any, params: Dict[str, Any], row_data: Dict[str, Any]) -> Tuple[bool, str]:
    """数组长度验证
    
    验证数组字段的元素数量在指定的最小和最大数量范围内。
    
    参数：
    - min: 最小元素数量（可选）
    - max: 最大元素数量（可选）
    - exact: 精确元素数量（可选，与min/max互斥）
    
    示例配置：
    { field = "RewardConfig", script = "array_length.py", params = { min = 1, max = 5 } }
    { field = "Tags", script = "array_length.py", params = { min = 1 } }
    { field = "Coordinates", script = "array_length.py", params = { exact = 2 } }
    { field = "Skills", script = "array_length.py", params = { max = 10 } }
    """
    
    # 如果值为空，跳过验证（由required.py处理必填验证）
    if value is None:
        return True, ""
    
    # 将值转换为列表进行验证
    if isinstance(value, list):
        array_value = value
    elif isinstance(value, str):
        # 如果是字符串，尝试按分隔符分割
        separator = params.get('separator', ',')
        if value.strip() == "":
            array_value = []
        else:
            array_value = [item.strip() for item in value.split(separator) if item.strip()]
    else:
        array_value = [value]
    
    array_length = len(array_value)
    
    # 精确数量验证
    exact_count = params.get('exact')
    if exact_count is not None:
        if array_length != exact_count:
            return False, f"Field '{field_name}' array length {array_length} does not match exact requirement {exact_count}"
        return True, ""
    
    # 范围验证
    min_length = params.get('min')
    max_length = params.get('max')
    
    if min_length is not None and array_length < min_length:
        return False, f"Field '{field_name}' array length {array_length} is less than minimum {min_length}"
    
    if max_length is not None and array_length > max_length:
        return False, f"Field '{field_name}' array length {array_length} is greater than maximum {max_length}"
    
    return True, ""