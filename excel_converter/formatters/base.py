"""基础格式化器

定义格式化器的抽象接口。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path


class BaseFormatter(ABC):
    """格式化器基类"""
    
    def __init__(self, encoding: str = 'utf-8'):
        self.encoding = encoding
    
    @property
    @abstractmethod
    def format_name(self) -> str:
        """格式名称"""
        pass
    
    @property
    @abstractmethod
    def file_extension(self) -> str:
        """文件扩展名"""
        pass
    
    @abstractmethod
    def format_data(self, data: Dict[str, Any], export_name: str) -> str:
        """格式化数据为字符串"""
        pass
    
    def save_to_file(self, formatted_data: str, output_path: Path) -> None:
        """保存格式化后的数据到文件"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding=self.encoding) as f:
            f.write(formatted_data)
    
    def get_output_filename(self, export_name: str) -> str:
        """生成输出文件名"""
        return f"{export_name}.{self.file_extension}"
    
    def validate_data(self, data: Dict[str, Any]) -> list[str]:
        """验证数据是否适合此格式化器"""
        errors = []
        
        if not isinstance(data, dict):
            errors.append("Data must be a dictionary")
        
        return errors