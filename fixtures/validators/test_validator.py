"""测试验证器

用于测试验证器引擎的功能。
"""

from typing import Dict, Any, Tuple, List


def validate_field(field_name: str, value: Any, params: Dict[str, Any], row_data: Dict[str, Any]) -> Tuple[bool, str]:
    """字段级验证 - 测试用"""
    
    # 测试参数
    min_value = params.get('min_value', 0)
    max_value = params.get('max_value', 9999)
    
    if field_name == "ID":
        # ID必须是正整数
        if not isinstance(value, int) or value <= 0:
            return False, f"ID must be a positive integer, got: {value}"
        
        # ID范围检查
        if value < min_value or value > max_value:
            return False, f"ID {value} out of range [{min_value}, {max_value}]"
    
    elif field_name == "Name":
        # 名称不能为空
        if not value or not isinstance(value, str):
            return False, f"Name cannot be empty, got: {value}"
        
        # 名称长度检查
        if len(value) < 2:
            return False, f"Name too short: {value}"
    
    return True, ""


def validate_row(row_data: Dict[str, Any], export_config: Dict[str, Any]) -> Tuple[bool, str]:
    """行级验证 - 测试用"""
    
    # 检查ID和Name的一致性（示例业务逻辑）
    item_id = row_data.get('ID')
    item_name = row_data.get('Name')
    
    if item_id and item_name:
        # 测试规则：ID为1001的必须是"测试剑"
        if item_id == 1001 and item_name != "测试剑":
            return False, f"ID 1001 must be named '测试剑', got: {item_name}"
    
    return True, ""


def validate_dataset(dataset: List[Dict[str, Any]], export_config: Dict[str, Any]) -> Tuple[bool, str]:
    """数据集级验证 - 测试用"""
    
    # 检查数据集不能为空
    if not dataset:
        return False, "Dataset cannot be empty"
    
    # 检查数据集大小限制（测试用）
    max_records = export_config.get('max_records', 100)
    if len(dataset) > max_records:
        return False, f"Too many records: {len(dataset)}, max allowed: {max_records}"
    
    # 检查ID唯一性
    ids = [row.get('ID') for row in dataset if row.get('ID')]
    if len(ids) != len(set(ids)):
        duplicates = [x for x in ids if ids.count(x) > 1]
        return False, f"Duplicate IDs found: {list(set(duplicates))}"
    
    return True, "" 