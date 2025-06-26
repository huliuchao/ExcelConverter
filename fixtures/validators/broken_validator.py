"""故意有错误的验证器

用于测试验证器引擎的错误处理功能。
"""

from typing import Dict, Any, Tuple


def validate_field(field_name: str, value: Any, params: Dict[str, Any], row_data: Dict[str, Any]) -> Tuple[bool, str]:
    """故意有错误的字段级验证"""
    
    # 故意引发异常
    if field_name == "ID":
        raise ValueError("This is a test error from broken validator")
    
    # 错误的返回值类型
    if field_name == "Name":
        return "invalid_return_type"  # 应该返回 (bool, str)
    
    return True, ""


# 故意缺少必需的函数参数
def validate_row(row_data):  # 缺少必需的参数
    """参数不正确的行级验证"""
    return True, ""


# 故意错误的函数签名
def validate_dataset():  # 完全错误的参数
    """参数错误的数据集级验证"""
    return True, "" 