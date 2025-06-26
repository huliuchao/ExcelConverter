"""配置管理器

负责加载、验证和管理TOML配置文件。
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import toml


@dataclass
class FieldConfig:
    """字段配置"""
    name: str
    type: Optional[str] = None  # 字段类型，优先级高于Excel中的类型定义
    scope: str = "sc"
    separator: Optional[str] = None


@dataclass
class ValidatorConfig:
    """验证器配置"""
    field: str
    script: str
    params: Optional[Dict[str, Any]] = None


@dataclass
class ObjectSchemaConfig:
    """对象Schema配置"""
    description: str
    separator: str = ","
    key_value_separator: str = ":"
    fields: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SourceConfig:
    """数据源配置"""
    file: str
    sheet: str


@dataclass
class InputConfig:
    """输入配置"""
    source_dir: str = "./excel"
    output_dir: str = "./output"
    file_pattern: str = "*.xlsx"


@dataclass
class OutputConfig:
    """输出配置"""
    format: str = "lua"
    encoding: str = "utf-8"


@dataclass
class ExportConfig:
    """导出配置"""
    sources: List[SourceConfig]
    scope: str
    primary_key: Optional[str] = None
    fields: List[FieldConfig] = field(default_factory=list)
    validators: List[ValidatorConfig] = field(default_factory=list)


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config_data: Dict[str, Any] = {}
        self.defaults: Dict[str, Any] = {}
        self.input_config: InputConfig = InputConfig()
        self.output_config: OutputConfig = OutputConfig()
        self.object_schemas: Dict[str, ObjectSchemaConfig] = {}
        self.exports: Dict[str, ExportConfig] = {}
    
    def load_config(self) -> None:
        """加载配置文件"""
        try:
            self.config_data = toml.load(self.config_path)
        except Exception as e:
            raise ValueError(f"Failed to load config file {self.config_path}: {e}")
        
        # 加载默认配置
        self.defaults = self.config_data.get('defaults', {})
        
        # 加载输入配置
        input_data = self.config_data.get('input', {})
        self.input_config = InputConfig(
            source_dir=input_data.get('source_dir', './excel'),
            output_dir=input_data.get('output_dir', './output'),
            file_pattern=input_data.get('file_pattern', '*.xlsx')
        )
        
        # 加载输出配置
        output_data = self.config_data.get('output', {})
        self.output_config = OutputConfig(
            format=output_data.get('format', 'lua'),
            encoding=output_data.get('encoding', 'utf-8')
        )
        
        # 加载对象schemas
        schemas_data = self.config_data.get('object_schemas', {})
        for name, schema_data in schemas_data.items():
            # 从 defaults 中获取默认的分隔符配置
            default_separator = self.defaults.get('separator', ',')
            default_key_value_separator = self.defaults.get('key_value_separator', ':')
            
            self.object_schemas[name] = ObjectSchemaConfig(
                description=schema_data.get('description', ''),
                separator=schema_data.get('separator', default_separator),
                key_value_separator=schema_data.get('key_value_separator', default_key_value_separator),
                fields=schema_data.get('fields', [])
            )
        
        # 加载导出配置
        exports_data = self.config_data.get('exports', {})
        for name, export_data in exports_data.items():
            # 解析数据源
            sources = []
            for source_data in export_data.get('sources', []):
                sources.append(SourceConfig(
                    file=source_data['file'],
                    sheet=source_data['sheet']
                ))
            
            # 解析字段配置
            fields = []
            for field_data in export_data.get('fields', []):
                if isinstance(field_data, str):
                    # 简单字符串格式
                    fields.append(FieldConfig(name=field_data))
                else:
                    # 完整配置格式
                    fields.append(FieldConfig(
                        name=field_data['name'],
                        type=field_data.get('type'),  # 支持类型配置
                        scope=field_data.get('scope', 'sc'),
                        separator=field_data.get('separator')
                    ))
            
            # 解析验证器配置
            validators = []
            for validator_data in export_data.get('validators', []):
                validators.append(ValidatorConfig(
                    field=validator_data['field'],
                    script=validator_data['script'],
                    params=validator_data.get('params')
                ))
            
            # 创建导出配置
            export_config = ExportConfig(
                sources=sources,
                scope=export_data['scope'],
                primary_key=export_data.get('primary_key'),
                fields=fields,
                validators=validators
            )
            
            # 应用默认值
            export_config = self.resolve_defaults(export_config)
            self.exports[name] = export_config
    
    def validate_config(self) -> List[str]:
        """验证配置文件的有效性"""
        errors = []
        
        # 验证必要的节存在
        if 'exports' not in self.config_data:
            errors.append("Missing required section: exports")
        
        # 验证每个导出配置
        for name, export_config in self.exports.items():
            if not export_config.sources:
                errors.append(f"Export '{name}': No sources specified")
            
            for source in export_config.sources:
                if not source.file:
                    errors.append(f"Export '{name}': Source file cannot be empty")
                if not source.sheet:
                    errors.append(f"Export '{name}': Source sheet cannot be empty")
            
            if export_config.scope not in ['s', 'c', 'sc']:
                errors.append(f"Export '{name}': Invalid scope '{export_config.scope}', must be 's', 'c', or 'sc'")
        
        return errors
    
    def get_export_config(self, export_name: str) -> Optional[ExportConfig]:
        """获取导出配置"""
        return self.exports.get(export_name)
    
    def get_object_schema(self, schema_name: str) -> Optional[ObjectSchemaConfig]:
        """获取对象schema配置"""
        return self.object_schemas.get(schema_name)
    
    def resolve_defaults(self, export_config: ExportConfig) -> ExportConfig:
        """解析默认值"""
        # 设置默认主键
        if export_config.primary_key is None:
            export_config.primary_key = self.defaults.get('primary_key', 'ID')
        
        # 设置字段默认分隔符
        default_separator = self.defaults.get('separator', ',')
        for field_config in export_config.fields:
            if field_config.separator is None:
                field_config.separator = default_separator
        
        return export_config
    
    def list_exports(self) -> List[str]:
        """列出所有导出配置名称"""
        return list(self.exports.keys())
    
    def get_default(self, key: str, default_value: Any = None) -> Any:
        """获取默认配置值"""
        return self.defaults.get(key, default_value)