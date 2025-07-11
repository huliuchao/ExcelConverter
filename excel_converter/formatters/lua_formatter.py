"""Lua格式化器

将数据转换为Lua表格式。
"""

from typing import Dict, Any, List, Union
from .base import BaseFormatter


class LuaFormatter(BaseFormatter):
    """Lua格式化器"""
    
    def __init__(self, encoding: str = 'utf-8', compact: bool = False):
        super().__init__(encoding)
        self.compact = compact
    
    @property
    def format_name(self) -> str:
        return "lua" + ("_compact" if self.compact else "")
    
    @property
    def file_extension(self) -> str:
        return "lua"
    
    def format_data(self, data: Dict[str, Any], export_name: str) -> str:
        """格式化数据为Lua格式"""
        lines = []
        
        if not self.compact:
            lines.append(f"-- {export_name} Data")
            lines.append(f"-- Auto-generated by Excel Converter")
            lines.append("")
        
        lines.append("return {")
        
        for key, value in data.items():
            formatted_value = self._format_lua_value(value, indent=1)
            if isinstance(key, str) and key.isidentifier():
                if self.compact:
                    lines.append(f"{key}={formatted_value},")
                else:
                    lines.append(f"    {key} = {formatted_value},")
            else:
                key_part = self._format_lua_value(key, indent=1)
                if self.compact:
                    lines.append(f"[{key_part}]={formatted_value},")
                else:
                    lines.append(f"    [{key_part}] = {formatted_value},")
        
        lines.append("}")
        
        if not self.compact:
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_lua_value(self, value: Any, indent: int = 0) -> str:
        """递归格式化Lua值"""
        if self.compact:
            return self._format_lua_value_compact(value, indent)
        else:
            return self._format_lua_value_readable(value, indent)
    
    def _format_lua_value_compact(self, value: Any, indent: int = 0) -> str:
        """紧凑模式格式化Lua值"""
        if value is None:
            return "nil"
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            return self._escape_lua_string(value)
        elif isinstance(value, list):
            if not value:
                return "{}"
            formatted_items = [self._format_lua_value_compact(item, indent) for item in value]
            return "{" + ",".join(formatted_items) + "}"
        elif isinstance(value, dict):
            if not value:
                return "{}"
            items = []
            for k, v in value.items():
                formatted_value = self._format_lua_value_compact(v, indent)
                if isinstance(k, str) and k.isidentifier():
                    items.append(f"{k}={formatted_value}")
                else:
                    formatted_key = self._format_lua_value_compact(k, indent)
                    items.append(f"[{formatted_key}]={formatted_value}")
            return "{" + ",".join(items) + "}"
        else:
            return self._escape_lua_string(str(value))
    
    def _format_lua_value_readable(self, value: Any, indent: int = 0) -> str:
        """可读模式格式化Lua值"""
        indent_str = "    " * indent
        
        if value is None:
            return "nil"
        
        elif isinstance(value, bool):
            return "true" if value else "false"
        
        elif isinstance(value, (int, float)):
            return str(value)
        
        elif isinstance(value, str):
            return self._escape_lua_string(value)
        
        elif isinstance(value, list):
            if not value:
                return "{}"
            
            if all(isinstance(item, (int, float, str, bool)) or item is None for item in value):
                formatted_items = [self._format_lua_value_readable(item) for item in value]
                return "{" + ", ".join(formatted_items) + "}"
            else:
                lines = ["{"]
                for item in value:
                    formatted_item = self._format_lua_value_readable(item, indent + 1)
                    lines.append(f"{indent_str}    {formatted_item},")
                lines.append(f"{indent_str}}}")
                return "\n".join(lines)
        
        elif isinstance(value, dict):
            if not value:
                return "{}"
            
            if all(isinstance(k, str) and k.isidentifier() and 
                   isinstance(v, (int, float, str, bool)) or v is None 
                   for k, v in value.items()):
                if len(value) <= 3:
                    items = []
                    for k, v in value.items():
                        formatted_value = self._format_lua_value_readable(v)
                        items.append(f"{k} = {formatted_value}")
                    return "{" + ", ".join(items) + "}"
            
            lines = ["{"]
            for k, v in value.items():
                formatted_value = self._format_lua_value_readable(v, indent + 1)
                if isinstance(k, str) and k.isidentifier():
                    lines.append(f"{indent_str}    {k} = {formatted_value},")
                else:
                    formatted_key = self._format_lua_value_readable(k)
                    lines.append(f"{indent_str}    [{formatted_key}] = {formatted_value},")
            lines.append(f"{indent_str}}}")
            return "\n".join(lines)
        
        else:
            return self._escape_lua_string(str(value))
    
    def _escape_lua_string(self, s: str) -> str:
        """转义Lua字符串"""
        if not s:
            return '""'
        
        if self._needs_escape(s):
            escaped = s.replace('\\', '\\\\')
            escaped = escaped.replace('"', '\\"')
            escaped = escaped.replace('\n', '\\n')
            escaped = escaped.replace('\r', '\\r')
            escaped = escaped.replace('\t', '\\t')
            return f'"{escaped}"'
        else:
            return f'"{s}"'
    
    def _needs_escape(self, s: str) -> bool:
        """检查字符串是否需要转义"""
        special_chars = ['\\', '"', '\n', '\r', '\t']
        return any(char in s for char in special_chars)
    
    def format_comment(self, text: str) -> str:
        """格式化注释"""
        lines = text.strip().split('\n')
        return '\n'.join(f"-- {line}" for line in lines)
    
    def format_multi_line_string(self, text: str) -> str:
        """格式化多行字符串（使用Lua的长字符串语法）"""
        level = 0
        delimiter = "=" * level
        while f"]{delimiter}]" in text:
            level += 1
            delimiter = "=" * level
        
        return f"[{delimiter}[{text}]{delimiter}]"