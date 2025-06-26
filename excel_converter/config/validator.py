"""配置验证器

负责验证配置文件的语法和语义正确性。
"""

from typing import List, Dict, Any
from pathlib import Path
import toml

from .config_manager import ExportConfig, ObjectSchemaConfig, ValidatorConfig


class ConfigValidator:
    """配置验证器"""
    
    def validate_toml_syntax(self, config_path: Path) -> List[str]:
        """验证TOML语法"""
        errors = []
        
        try:
            toml.load(config_path)
        except toml.TomlDecodeError as e:
            errors.append(f"TOML syntax error: {e}")
        except Exception as e:
            errors.append(f"Error reading config file: {e}")
        
        return errors
    
    def validate_export_config(self, export_config: ExportConfig) -> List[str]:
        """验证导出配置"""
        errors = []
        
        # 验证数据源
        if not export_config.sources:
            errors.append("No sources specified")
        
        for i, source in enumerate(export_config.sources):
            if not source.file.strip():
                errors.append(f"Source {i+1}: File path cannot be empty")
            if not source.sheet.strip():
                errors.append(f"Source {i+1}: Sheet name cannot be empty")
        
        # 验证作用域
        if export_config.scope not in ['s', 'c', 'sc']:
            errors.append(f"Invalid scope '{export_config.scope}', must be 's', 'c', or 'sc'")
        
        # 验证主键
        if not export_config.primary_key or not export_config.primary_key.strip():
            errors.append("Primary key cannot be empty")
        
        # 验证字段配置
        field_names = set()
        for field in export_config.fields:
            if not field.name.strip():
                errors.append("Field name cannot be empty")
            
            if field.name in field_names:
                errors.append(f"Duplicate field name: {field.name}")
            field_names.add(field.name)
            
            if field.scope not in ['s', 'c', 'sc']:
                errors.append(f"Field '{field.name}': Invalid scope '{field.scope}', must be 's', 'c', or 'sc'")
        
        return errors
    
    def validate_object_schemas(self, schemas: Dict[str, ObjectSchemaConfig]) -> List[str]:
        """验证对象schema配置"""
        errors = []
        
        for schema_name, schema in schemas.items():
            if not schema_name.strip():
                errors.append("Object schema name cannot be empty")
            
            if not schema.description.strip():
                errors.append(f"Schema '{schema_name}': Description cannot be empty")
            
            if not schema.separator:
                errors.append(f"Schema '{schema_name}': Separator cannot be empty")
            
            if not schema.key_value_separator:
                errors.append(f"Schema '{schema_name}': Key-value separator cannot be empty")
            
            # 验证字段定义
            field_keys = set()
            for field in schema.fields:
                if 'key' not in field:
                    errors.append(f"Schema '{schema_name}': Field missing 'key' property")
                    continue
                
                field_key = field['key']
                if not field_key.strip():
                    errors.append(f"Schema '{schema_name}': Field key cannot be empty")
                
                if field_key in field_keys:
                    errors.append(f"Schema '{schema_name}': Duplicate field key: {field_key}")
                field_keys.add(field_key)
                
                if 'type' not in field:
                    errors.append(f"Schema '{schema_name}': Field '{field_key}' missing 'type' property")
                else:
                    field_type = field['type']
                    if field_type not in ['int', 'float', 'string', 'bool']:
                        errors.append(f"Schema '{schema_name}': Field '{field_key}' has invalid type '{field_type}'")
        
        return errors
    
    def validate_validator_scripts(self, validators: List[ValidatorConfig], validator_dir: Path) -> List[str]:
        """验证验证器脚本是否存在"""
        errors = []
        
        if not validator_dir.exists():
            errors.append(f"Validator directory does not exist: {validator_dir}")
            return errors
        
        for validator in validators:
            script_path = validator_dir / validator.script
            
            if not script_path.exists():
                errors.append(f"Validator script not found: {script_path}")
            elif not script_path.is_file():
                errors.append(f"Validator script is not a file: {script_path}")
            elif not script_path.suffix == '.py':
                errors.append(f"Validator script must be a Python file: {script_path}")
        
        return errors
    
    def validate_file_dependencies(self, export_configs: Dict[str, ExportConfig], excel_dir: Path) -> List[str]:
        """验证Excel文件依赖是否存在"""
        errors = []
        
        if not excel_dir.exists():
            errors.append(f"Excel directory does not exist: {excel_dir}")
            return errors
        
        for export_name, config in export_configs.items():
            for source in config.sources:
                excel_path = excel_dir / source.file
                
                if not excel_path.exists():
                    errors.append(f"Export '{export_name}': Excel file not found: {excel_path}")
                elif not excel_path.is_file():
                    errors.append(f"Export '{export_name}': Excel path is not a file: {excel_path}")
                elif excel_path.suffix.lower() not in ['.xlsx', '.xls']:
                    errors.append(f"Export '{export_name}': File is not an Excel file: {excel_path}")
        
        return errors
    
    def validate_cross_references(self, config_data: Dict[str, Any]) -> List[str]:
        """验证配置项之间的交叉引用"""
        errors = []
        
        object_schemas = set(config_data.get('object_schemas', {}).keys())
        exports = config_data.get('exports', {})
        
        for export_name, export_data in exports.items():
            fields = export_data.get('fields', [])
            
            for field in fields:
                # 如果字段有类型定义，检查对象类型引用
                field_type = field.get('type', '')
                if field_type.startswith('object:'):
                    schema_name = field_type[7:]  # 去掉 'object:' 前缀
                    if schema_name not in object_schemas:
                        errors.append(f"Export '{export_name}': Field '{field.get('name', '')}' references undefined object schema: {schema_name}")
        
        return errors