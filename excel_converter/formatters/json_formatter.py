"""JSON格式化器

将数据转换为JSON格式。
"""

import json
from typing import Dict, Any
from .base import BaseFormatter


class JsonFormatter(BaseFormatter):
    """JSON格式化器"""
    
    def __init__(self, encoding: str = 'utf-8', indent: int = 4, ensure_ascii: bool = False):
        super().__init__(encoding)
        self.indent = indent
        self.ensure_ascii = ensure_ascii
    
    @property
    def format_name(self) -> str:
        return "json"
    
    @property
    def file_extension(self) -> str:
        return "json"
    
    def format_data(self, data: Dict[str, Any], export_name: str) -> str:
        """格式化数据为JSON格式"""
        # 创建包含元数据的JSON结构
        json_data = {
            "_metadata": {
                "export_name": export_name,
                "generated_by": "Excel Converter",
                "format": "json"
            },
            "data": data
        }
        
        try:
            return json.dumps(
                json_data,
                ensure_ascii=self.ensure_ascii,
                indent=self.indent,
                separators=(',', ': '),
                sort_keys=False
            )
        except (TypeError, ValueError) as e:
            cleaned_data = self._clean_data_for_json(data)
            json_data["data"] = cleaned_data
            
            return json.dumps(
                json_data,
                ensure_ascii=self.ensure_ascii,
                indent=self.indent,
                separators=(',', ': '),
                sort_keys=False
            )
    
    def _clean_data_for_json(self, data: Any) -> Any:
        """清理数据以确保JSON兼容性"""
        if isinstance(data, dict):
            return {str(k): self._clean_data_for_json(v) for k, v in data.items()}
        
        elif isinstance(data, list):
            return [self._clean_data_for_json(item) for item in data]
        
        elif isinstance(data, (str, int, float, bool)) or data is None:
            return data
        
        else:
            return str(data)
    
    def format_compact(self, data: Dict[str, Any], export_name: str) -> str:
        """格式化为紧凑的JSON格式（无缩进）"""
        json_data = {
            "_metadata": {
                "export_name": export_name,
                "generated_by": "Excel Converter",
                "format": "json"
            },
            "data": data
        }
        
        try:
            return json.dumps(
                json_data,
                ensure_ascii=self.ensure_ascii,
                separators=(',', ':')
            )
        except (TypeError, ValueError):
            cleaned_data = self._clean_data_for_json(data)
            json_data["data"] = cleaned_data
            
            return json.dumps(
                json_data,
                ensure_ascii=self.ensure_ascii,
                separators=(',', ':')
            )
    
    def format_data_only(self, data: Dict[str, Any], export_name: str) -> str:
        """格式化为纯数据JSON（不包含元数据）"""
        try:
            return json.dumps(
                data,
                ensure_ascii=self.ensure_ascii,
                indent=self.indent,
                separators=(',', ': '),
                sort_keys=False
            )
        except (TypeError, ValueError):
            cleaned_data = self._clean_data_for_json(data)
            return json.dumps(
                cleaned_data,
                ensure_ascii=self.ensure_ascii,
                indent=self.indent,
                separators=(',', ': '),
                sort_keys=False
            )
    
    def format_array(self, data: Dict[str, Any], export_name: str) -> str:
        """格式化为数组格式的JSON（将字典值转换为数组）"""
        array_data = list(data.values())
        
        try:
            return json.dumps(
                array_data,
                ensure_ascii=self.ensure_ascii,
                indent=self.indent,
                separators=(',', ': '),
                sort_keys=False
            )
        except (TypeError, ValueError):
            cleaned_data = [self._clean_data_for_json(item) for item in array_data]
            
            return json.dumps(
                cleaned_data,
                ensure_ascii=self.ensure_ascii,
                indent=self.indent,
                separators=(',', ': '),
                sort_keys=False
            )
    
    def validate_json_compatibility(self, data: Any) -> list[str]:
        """验证数据是否JSON兼容"""
        errors = []
        
        try:
            json.dumps(data)
        except TypeError as e:
            errors.append(f"Data contains non-JSON-serializable types: {e}")
        except ValueError as e:
            errors.append(f"Data contains invalid values: {e}")
        
        return errors