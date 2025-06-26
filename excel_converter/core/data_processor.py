"""数据处理器

负责处理Excel数据，包括类型转换、作用域过滤等。
"""

from typing import List, Dict, Any
from .type_system import TypeSystem
from .excel_reader import ExcelData
from ..config.config_manager import ExportConfig, FieldConfig
from ..utils.scope_utils import field_matches_scope


class DataProcessor:
    """数据处理器"""
    
    def __init__(self, type_system: TypeSystem):
        self.type_system = type_system
    
    def process_data(self, excel_data: ExcelData, export_config: ExportConfig) -> Dict[str, Any]:
        """处理Excel数据"""
        processed_rows = []
        
        for row in excel_data.rows:
            processed_row = {}
            
            for field in excel_data.fields:
                if field.name in row:
                    # 查找字段配置
                    field_config = self._find_field_config(field.name, export_config.fields)
                    
                    # 应用作用域过滤
                    if field_config and not field_matches_scope(field_config.scope, export_config.scope):
                        continue
                    
                    # 确定字段类型：优先使用配置中的type，否则使用Excel中的type
                    field_type = (field_config.type if field_config and field_config.type 
                                 else field.type)
                    
                    # 类型转换
                    separator = field_config.separator if field_config else ','
                    converted_value = self.type_system.convert_value(
                        row[field.name], 
                        field_type, 
                        separator=separator
                    )
                    processed_row[field.name] = converted_value
            
            if processed_row:
                processed_rows.append(processed_row)
        
        # 转换为主键字典
        return self._convert_to_primary_key_dict(processed_rows, export_config.primary_key)
    
    def _find_field_config(self, field_name: str, field_configs: List[FieldConfig]) -> FieldConfig:
        """查找字段配置"""
        for field_config in field_configs:
            if field_config.name == field_name:
                return field_config
        return None
    
    def _convert_to_primary_key_dict(self, rows: List[Dict[str, Any]], primary_key: str) -> Dict[str, Any]:
        """转换为以主键为key的字典"""
        result = {}
        
        for row in rows:
            if primary_key in row:
                key = row[primary_key]
                result[key] = row
            else:
                # 如果没有主键，使用行索引
                key = len(result)
                result[key] = row
        
        return result