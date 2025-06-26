"""数据合并器

负责合并多个Excel数据源的数据。
"""

from typing import List, Dict, Any
from .excel_reader import ExcelData
from ..config.config_manager import ExportConfig
from ..utils.error_handler import ConversionError


class DataMerger:
    """数据合并器"""
    
    def merge_data_sources(self, excel_data_list: List[ExcelData], export_config: ExportConfig) -> Dict[str, Any]:
        """合并多个数据源"""
        if not excel_data_list:
            return {}
        
        # 验证schema兼容性
        schema_errors = self._validate_schema_compatibility(excel_data_list)
        if schema_errors:
            raise ConversionError(f"Schema compatibility errors: {'; '.join(schema_errors)}")
        
        # 收集所有数据行
        all_rows = []
        for excel_data in excel_data_list:
            all_rows.extend(excel_data.rows)
        
        # 检查主键冲突
        primary_key = export_config.primary_key
        conflicts = self._check_primary_key_conflicts(all_rows, primary_key)
        if conflicts:
            raise ConversionError(f"Primary key conflicts: {'; '.join(conflicts)}")
        
        # 合并数据
        merged_data = {}
        for row in all_rows:
            if primary_key in row and row[primary_key] is not None:
                key = row[primary_key]
                merged_data[key] = row
        
        return merged_data
    
    def _validate_schema_compatibility(self, excel_data_list: List[ExcelData]) -> List[str]:
        """验证多个数据源的字段兼容性"""
        errors = []
        
        if len(excel_data_list) <= 1:
            return errors
        
        # 以第一个数据源为基准
        base_fields = {field.name: field.type for field in excel_data_list[0].fields}
        
        for i, excel_data in enumerate(excel_data_list[1:], 1):
            current_fields = {field.name: field.type for field in excel_data.fields}
            
            # 检查共同字段的类型是否一致
            for field_name, field_type in current_fields.items():
                if field_name in base_fields:
                    if base_fields[field_name] != field_type:
                        errors.append(
                            f"Field '{field_name}' type mismatch: "
                            f"source 0 has '{base_fields[field_name]}', "
                            f"source {i} has '{field_type}'"
                        )
        
        return errors
    
    def validate_schema_with_config_types(self, excel_data_list: List[ExcelData], 
                                         export_config: ExportConfig) -> List[str]:
        """基于配置类型验证多个数据源的字段兼容性
        
        如果配置中定义了字段类型，则忽略Excel中的类型差异
        """
        errors = []
        
        if len(excel_data_list) <= 1:
            return errors
        
        # 构建配置类型映射
        config_types = {}
        for field_config in export_config.fields:
            if field_config.type:
                config_types[field_config.name] = field_config.type
        
        # 以第一个数据源为基准
        base_fields = {field.name: field.type for field in excel_data_list[0].fields}
        
        for i, excel_data in enumerate(excel_data_list[1:], 1):
            current_fields = {field.name: field.type for field in excel_data.fields}
            
            # 检查共同字段的类型是否一致
            for field_name, field_type in current_fields.items():
                if field_name in base_fields:
                    # 如果配置中定义了类型，则跳过Excel类型检查
                    if field_name in config_types:
                        continue
                    
                    # 否则检查Excel类型是否一致
                    if base_fields[field_name] != field_type:
                        errors.append(
                            f"Field '{field_name}' type mismatch: "
                            f"source 0 has '{base_fields[field_name]}', "
                            f"source {i} has '{field_type}'. "
                            f"Consider defining type in config to override Excel types."
                        )
        
        return errors
    
    def _check_primary_key_conflicts(self, all_rows: List[Dict[str, Any]], primary_key: str) -> List[str]:
        """检查主键冲突"""
        conflicts = []
        seen_keys = set()
        
        for i, row in enumerate(all_rows):
            if primary_key in row and row[primary_key] is not None:
                key = row[primary_key]
                if key in seen_keys:
                    conflicts.append(f"Duplicate primary key '{key}' at row {i+1}")
                else:
                    seen_keys.add(key)
        
        return conflicts
    
    def get_merge_statistics(self, excel_data_list: List[ExcelData]) -> Dict[str, Any]:
        """获取合并统计信息"""
        total_sources = len(excel_data_list)
        total_rows = sum(len(data.rows) for data in excel_data_list)
        
        # 统计字段信息
        all_fields = set()
        for excel_data in excel_data_list:
            for field in excel_data.fields:
                all_fields.add(field.name)
        
        return {
            "total_sources": total_sources,
            "total_rows": total_rows,
            "unique_fields": len(all_fields),
            "field_names": sorted(all_fields)
        }