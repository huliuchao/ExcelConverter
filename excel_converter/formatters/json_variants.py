"""JSON格式变体

提供JSON格式化器的不同变体（原始数据、数组格式），支持紧凑模式参数。
"""

import json
from typing import Dict, Any
from .json_formatter import JsonFormatter


class JsonMapFormatter(JsonFormatter):
    """映射JSON格式化器 - 键值对结构，不包含元数据"""
    
    def __init__(self, encoding: str = 'utf-8', indent: int = 4, ensure_ascii: bool = False, compact: bool = False):
        super().__init__(encoding, indent if not compact else None, ensure_ascii)
        self.compact = compact
    
    @property
    def format_name(self) -> str:
        return "json_map" + ("_compact" if self.compact else "")
    
    def get_output_filename(self, export_name: str) -> str:
        """生成输出文件名"""
        # suffix = "_compact" if self.compact else ""
        # return f"{export_name}_raw{suffix}.{self.file_extension}"
        return f"{export_name}.{self.file_extension}"
    
    def format_data(self, data: Dict[str, Any], export_name: str) -> str:
        """使用映射格式，支持紧凑模式"""
        if self.compact:
            # 使用紧凑格式
            try:
                return json.dumps(
                    data,
                    ensure_ascii=self.ensure_ascii,
                    separators=(',', ':')
                )
            except (TypeError, ValueError):
                cleaned_data = self._clean_data_for_json(data)
                return json.dumps(
                    cleaned_data,
                    ensure_ascii=self.ensure_ascii,
                    separators=(',', ':')
                )
        else:
            # 使用标准缩进格式
            return self.format_data_only(data, export_name)


class JsonArrayFormatter(JsonFormatter):
    """数组JSON格式化器 - 将数据转换为数组格式"""
    
    def __init__(self, encoding: str = 'utf-8', indent: int = 4, ensure_ascii: bool = False, compact: bool = False):
        super().__init__(encoding, indent if not compact else None, ensure_ascii)
        self.compact = compact
    
    @property
    def format_name(self) -> str:
        return "json_array" + ("_compact" if self.compact else "")
    
    def get_output_filename(self, export_name: str) -> str:
        """生成输出文件名"""
        # suffix = "_compact" if self.compact else ""
        # return f"{export_name}_array{suffix}.{self.file_extension}"
        return f"{export_name}.{self.file_extension}"
    
    def format_data(self, data: Dict[str, Any], export_name: str) -> str:
        """使用数组格式，支持紧凑模式"""
        # 将字典转换为数组格式
        array_data = list(data.values())
        
        if self.compact:
            # 使用紧凑格式
            try:
                return json.dumps(
                    array_data,
                    ensure_ascii=self.ensure_ascii,
                    separators=(',', ':')
                )
            except (TypeError, ValueError):
                cleaned_data = [self._clean_data_for_json(item) for item in array_data]
                return json.dumps(
                    cleaned_data,
                    ensure_ascii=self.ensure_ascii,
                    separators=(',', ':')
                )
        else:
            # 使用标准缩进格式
            return self.format_array(data, export_name)


class JsonPackedFormatter(JsonFormatter):
    """打包JSON格式化器 - 保留主键，其他数据打包为JSON字符串"""
    
    def __init__(self, encoding: str = 'utf-8', indent: int = 4, ensure_ascii: bool = False, compact: bool = False, primary_key: str = 'ID'):
        super().__init__(encoding, indent if not compact else None, ensure_ascii)
        self.compact = compact
        self.primary_key = primary_key
    
    @property
    def format_name(self) -> str:
        return "json_packed" + ("_compact" if self.compact else "")
    
    def get_output_filename(self, export_name: str) -> str:
        """生成输出文件名"""
        return f"{export_name}.{self.file_extension}"
    
    def format_data(self, data: Dict[str, Any], export_name: str) -> str:
        """将数据格式化为打包JSON数组格式"""
        packed_array = []
        
        for key, row in data.items():
            if not isinstance(row, dict):
                continue
                
            packed_row = {}
            primary_key_value = row.get(self.primary_key)
            if primary_key_value is not None:
                packed_row[self.primary_key] = primary_key_value
            
            other_fields = {k: v for k, v in row.items() if k != self.primary_key}
            if other_fields:
                try:
                    cleaned_other_fields = self._clean_data_for_json(other_fields)
                    
                    if self.compact:
                        packed_row['data'] = json.dumps(
                            cleaned_other_fields,
                            ensure_ascii=self.ensure_ascii,
                            separators=(',', ':')
                        )
                    else:
                        packed_row['data'] = json.dumps(
                            cleaned_other_fields,
                            ensure_ascii=self.ensure_ascii,
                            separators=(',', ': ')
                        )
                except (TypeError, ValueError):
                    packed_row['data'] = str(other_fields)
            
            packed_array.append(packed_row)
        
        if self.compact:
            try:
                return json.dumps(
                    packed_array,
                    ensure_ascii=self.ensure_ascii,
                    separators=(',', ':')
                )
            except (TypeError, ValueError):
                cleaned_data = [self._clean_data_for_json(item) for item in packed_array]
                return json.dumps(
                    cleaned_data,
                    ensure_ascii=self.ensure_ascii,
                    separators=(',', ':')
                )
        else:
            try:
                return json.dumps(
                    packed_array,
                    ensure_ascii=self.ensure_ascii,
                    indent=self.indent,
                    separators=(',', ': '),
                    sort_keys=False
                )
            except (TypeError, ValueError):
                cleaned_data = [self._clean_data_for_json(item) for item in packed_array]
                return json.dumps(
                    cleaned_data,
                    ensure_ascii=self.ensure_ascii,
                    indent=self.indent,
                    separators=(',', ': '),
                    sort_keys=False
                )