"""作用域工具模块

提供作用域相关的通用工具函数。
"""


def field_matches_scope(field_scope: str, export_scope: str) -> bool:
    """检查字段作用域是否匹配导出作用域
    
    Args:
        field_scope: 字段作用域 ('s', 'c', 'sc')
        export_scope: 导出作用域 ('s', 'c', 'sc')
    
    Returns:
        bool: 是否匹配
    """
    if export_scope == 'sc':
        return True
    elif export_scope == 's':
        return field_scope in ['s', 'sc']
    elif export_scope == 'c':
        return field_scope in ['c', 'sc']
    else:
        return False