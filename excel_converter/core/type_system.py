"""类型系统

提供各种数据类型的转换功能，包括基本类型、数组类型和自定义对象类型。
"""

from typing import Any, Dict, List, Union
from abc import ABC, abstractmethod
import re

from ..config.config_manager import ObjectSchemaConfig
from ..utils.error_handler import ConversionError


class TypeConverter(ABC):
    """类型转换器基类"""
    
    @abstractmethod
    def convert(self, value: Any, **kwargs) -> Any:
        """转换值"""
        pass


class BasicTypeConverter(TypeConverter):
    """基本类型转换器"""
    
    def convert(self, value: Any, target_type: str) -> Any:
        """转换基本类型：int, float, string, bool"""
        if value is None:
            return None
        
        try:
            if target_type == 'int':
                if isinstance(value, (int, float)):
                    return int(value)
                return int(str(value).strip())
            
            elif target_type == 'float':
                if isinstance(value, (int, float)):
                    return float(value)
                return float(str(value).strip())
            
            elif target_type == 'bool':
                if isinstance(value, bool):
                    return value
                str_value = str(value).strip().lower()
                return str_value in ['true', '1', 'yes', 'on', '是', '真']
            
            elif target_type == 'string':
                return str(value).strip()
            
            else:
                raise ConversionError(f"Unknown basic type: {target_type}")
        
        except (ValueError, TypeError) as e:
            raise ConversionError(f"Failed to convert '{value}' to {target_type}: {e}")


class ArrayTypeConverter(TypeConverter):
    """数组类型转换器"""
    
    def __init__(self, basic_converter: BasicTypeConverter, type_system=None):
        self.basic_converter = basic_converter
        self.type_system = type_system
    
    def set_type_system(self, type_system):
        """设置TypeSystem引用以处理复杂类型"""
        self.type_system = type_system
    
    def convert(self, value: Any, element_type: str, separator: str = ",") -> List[Any]:
        """转换数组类型：array<int>, array<string>, array<object:attribute>等"""
        if value is None:
            return []
        
        if isinstance(value, list):
            return [self._convert_element(item, element_type) for item in value]
        
        str_value = str(value).strip()
        if not str_value:
            return []
        
        parts = [part.strip() for part in str_value.split(separator)]
        
        result = []
        for part in parts:
            if part:  # 忽略空字符串
                converted = self._convert_element(part, element_type)
                result.append(converted)
        
        return result
    
    def _convert_element(self, value: Any, element_type: str) -> Any:
        """转换单个数组元素"""
        if element_type in ['int', 'float', 'string', 'bool']:
            return self.basic_converter.convert(value, element_type)
        
        if self.type_system:
            return self.type_system.convert_value(value, element_type)
        
        return str(value).strip()


class ObjectTypeConverter(TypeConverter):
    """自定义对象类型转换器"""
    
    def __init__(self, object_schemas: Dict[str, ObjectSchemaConfig], basic_converter: BasicTypeConverter):
        self.object_schemas = object_schemas
        self.basic_converter = basic_converter
    
    def convert(self, value: Any, schema_name: str) -> Dict[str, Any]:
        """转换自定义对象类型"""
        if value is None:
            return {}
        
        if schema_name not in self.object_schemas:
            raise ConversionError(f"Unknown object schema: {schema_name}")
        
        schema = self.object_schemas[schema_name]
        str_value = str(value).strip()
        
        if not str_value:
            return {}
        
        # 检测是否为key-value格式
        if schema.key_value_separator in str_value:
            return self._parse_key_value_pairs(str_value, schema)
        else:
            return self._parse_ordered_values(str_value, schema)
    
    def _parse_ordered_values(self, value: str, schema: ObjectSchemaConfig) -> Dict[str, Any]:
        """解析按顺序填写的值"""
        parts = [part.strip() for part in value.split(schema.separator)]
        result = {}
        
        for i, field_def in enumerate(schema.fields):
            field_key = field_def['key']
            field_type = field_def['type']
            
            if i < len(parts) and parts[i]:
                try:
                    converted_value = self.basic_converter.convert(parts[i], field_type)
                    result[field_key] = converted_value
                except Exception as e:
                    raise ConversionError(f"Failed to convert field '{field_key}' value '{parts[i]}': {e}")
        
        return result
    
    def _parse_key_value_pairs(self, value: str, schema: ObjectSchemaConfig) -> Dict[str, Any]:
        """解析key-value格式的值"""
        pairs = [pair.strip() for pair in value.split(schema.separator)]
        result = {}
        
        field_types = {field['key']: field['type'] for field in schema.fields}
        
        for pair in pairs:
            if not pair:
                continue
            
            if schema.key_value_separator not in pair:
                raise ConversionError(f"Invalid key-value pair format: '{pair}'. Expected format: key{schema.key_value_separator}value")
            
            key, val = pair.split(schema.key_value_separator, 1)
            key = key.strip()
            val = val.strip()
            
            if key not in field_types:
                raise ConversionError(f"Unknown field key '{key}' in schema '{schema}'")
            
            field_type = field_types[key]
            
            try:
                converted_value = self.basic_converter.convert(val, field_type)
                result[key] = converted_value
            except Exception as e:
                raise ConversionError(f"Failed to convert field '{key}' value '{val}': {e}")
        
        return result


class TypeSystem:
    """类型系统主类"""
    
    def __init__(self, object_schemas: Dict[str, ObjectSchemaConfig]):
        self.basic_converter = BasicTypeConverter()
        self.array_converter = ArrayTypeConverter(self.basic_converter)
        self.object_converter = ObjectTypeConverter(object_schemas, self.basic_converter)
        
        self.array_converter.set_type_system(self)
        
        self.array_pattern = re.compile(r'^array<(.+)>$')
        self.object_pattern = re.compile(r'^object:(.+)$')
    
    def convert_value(self, value: Any, type_def: str, **kwargs) -> Any:
        """根据类型定义转换值"""
        if value is None:
            return None
        
        type_def = type_def.strip()
        
        # 基本类型
        if type_def in ['int', 'float', 'string', 'bool']:
            return self.basic_converter.convert(value, type_def)
        
        # 数组类型
        array_match = self.array_pattern.match(type_def)
        if array_match:
            element_type = array_match.group(1)
            separator = kwargs.get('separator', ',')
            return self.array_converter.convert(value, element_type, separator)
        
        # 对象类型
        object_match = self.object_pattern.match(type_def)
        if object_match:
            schema_name = object_match.group(1)
            return self.object_converter.convert(value, schema_name)
        
        # 未知类型
        return str(value).strip()
    
    def validate_type_definition(self, type_def: str) -> List[str]:
        """验证类型定义的有效性"""
        errors = []
        
        type_def = type_def.strip()
        
        # 基本类型
        if type_def in ['int', 'float', 'string', 'bool']:
            return errors
        
        # 数组类型
        array_match = self.array_pattern.match(type_def)
        if array_match:
            element_type = array_match.group(1)
            nested_errors = self.validate_type_definition(element_type)
            if nested_errors:
                errors.extend([f"Array element type error: {error}" for error in nested_errors])
            return errors
        
        # 对象类型
        object_match = self.object_pattern.match(type_def)
        if object_match:
            schema_name = object_match.group(1)
            if schema_name not in self.object_converter.object_schemas:
                errors.append(f"Object schema '{schema_name}' not found")
            return errors
        
        errors.append(f"Unknown type definition: '{type_def}'")
        return errors
    
    def get_supported_types(self) -> Dict[str, List[str]]:
        """获取支持的类型列表"""
        return {
            'basic': ['int', 'float', 'string', 'bool'],
            'array': ['array<int>', 'array<float>', 'array<string>', 'array<bool>'] + 
                    [f'array<object:{name}>' for name in self.object_converter.object_schemas.keys()],
            'object': [f'object:{name}' for name in self.object_converter.object_schemas.keys()]
        }
    
    def infer_type_from_value(self, value: Any) -> str:
        """从值推断类型"""
        if value is None:
            return 'string'
        
        if isinstance(value, bool):
            return 'bool'
        elif isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, list):
            if value:
                element_type = self.infer_type_from_value(value[0])
                return f'array<{element_type}>'
            else:
                return 'array<string>'
        elif isinstance(value, dict):
            return 'object:unknown'
        else:
            str_value = str(value).strip()
            
            try:
                int(str_value)
                return 'int'
            except ValueError:
                pass
            
            try:
                float(str_value)
                return 'float'
            except ValueError:
                pass
            
            if str_value.lower() in ['true', 'false', '1', '0', 'yes', 'no']:
                return 'bool'
            
            if ',' in str_value:
                return f'array<string>'
            
            return 'string'