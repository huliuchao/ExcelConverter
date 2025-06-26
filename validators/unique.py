"""唯一性验证器

验证字段值在整个数据集中是否唯一。
"""

from typing import Dict, Any, Tuple, List, Set


def validate_dataset(dataset: List[Dict[str, Any]], export_config: Dict[str, Any]) -> Tuple[bool, str]:
    """数据集级唯一性验证
    
    检查所有使用 unique.py 的字段在整个数据集中是否唯一。
    
    参数：
    - check_null: 是否检查空值的唯一性（默认 False，跳过空值）
    
    示例配置：
    { field = "ID", script = "unique.py" }
    { field = "Email", script = "unique.py", params = { check_null = true } }
    """
    
    # 获取所有使用 unique.py 的验证器配置
    validators = export_config.get('validators', [])
    print(validators)
    unique_fields = []
    
    for validator in validators:
        # 处理 ValidatorConfig 对象或字典
        if hasattr(validator, 'script'):
            # ValidatorConfig 对象
            if validator.script == 'unique.py':
                field_name = validator.field
                params = validator.params or {}
                unique_fields.append((field_name, params))
        elif isinstance(validator, dict):
            # 字典对象
            if validator.get('script') == 'unique.py':
                field_name = validator.get('field')
                params = validator.get('params', {})
                unique_fields.append((field_name, params))
    
    # 检查每个需要唯一性验证的字段
    all_errors = []
    for field_name, params in unique_fields:
        success, message = _check_field_uniqueness(field_name, dataset, params)
        if not success:
            all_errors.append(message)
    
    if all_errors:
        return False, "; ".join(all_errors)
    
    return True, ""


def validate_field(field_name: str, value: Any, params: Dict[str, Any], row_data: Dict[str, Any]) -> Tuple[bool, str]:
    """字段级验证（唯一性检查在数据集级别进行）
    
    字段级验证总是通过，实际的唯一性检查在 validate_dataset 中进行。
    """
    return True, ""


def _check_field_uniqueness(field_name: str, dataset: List[Dict[str, Any]], params: Dict[str, Any]) -> Tuple[bool, str]:
    """检查指定字段的唯一性
    
    这是一个辅助函数，用于实际的唯一性检查。
    """
    seen_values: Set[Any] = set()
    duplicates = []
    
    check_null = params.get('check_null', False)
    
    for i, row in enumerate(dataset):
        value = row.get(field_name)
        
        # 跳过空值的唯一性检查（除非明确要求检查空值）
        if not check_null and (value is None or str(value).strip() == ""):
            continue
        
        if value in seen_values:
            duplicates.append(f"Row {i+1}: '{value}'")
        else:
            seen_values.add(value)
    
    if duplicates:
        return False, f"Field '{field_name}' has duplicate values: {', '.join(duplicates)}"
    
    return True, ""