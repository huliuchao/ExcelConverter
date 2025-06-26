"""文件操作工具

提供文件和目录操作的工具函数。
"""

from pathlib import Path
from typing import Optional
import os


def ensure_directory(path: Path) -> None:
    """确保目录存在，如果不存在则创建"""
    path.mkdir(parents=True, exist_ok=True)


def get_file_extension(file_path: Path) -> str:
    """获取文件扩展名（不包含点）"""
    return file_path.suffix.lstrip('.').lower()


def is_excel_file(file_path: Path) -> bool:
    """检查是否为Excel文件"""
    return get_file_extension(file_path) in ['xlsx', 'xls']


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除不安全字符"""
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    filename = filename.strip(' .')
    
    if not filename:
        filename = 'unnamed'
    
    return filename


def get_relative_path(file_path: Path, base_path: Path) -> Path:
    """获取相对于base_path的相对路径"""
    try:
        return file_path.relative_to(base_path)
    except ValueError:
        return file_path


def find_files_by_pattern(directory: Path, pattern: str) -> list[Path]:
    """在目录中查找匹配模式的文件"""
    if not directory.exists() or not directory.is_dir():
        return []
    
    return list(directory.glob(pattern))


def get_file_size_mb(file_path: Path) -> float:
    """获取文件大小（MB）"""
    if not file_path.exists():
        return 0.0
    
    size_bytes = file_path.stat().st_size
    return size_bytes / (1024 * 1024)


def backup_file(file_path: Path, backup_suffix: str = '.bak') -> Optional[Path]:
    """备份文件"""
    if not file_path.exists():
        return None
    
    backup_path = file_path.with_suffix(file_path.suffix + backup_suffix)
    
    counter = 1
    while backup_path.exists():
        backup_path = file_path.with_suffix(f"{file_path.suffix}{backup_suffix}.{counter}")
        counter += 1
    
    try:
        import shutil
        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception:
        return None


def ensure_file_writable(file_path: Path) -> bool:
    """确保文件可写"""
    try:
        if file_path.exists():
            return os.access(file_path, os.W_OK)
        else:
            parent_dir = file_path.parent
            return parent_dir.exists() and os.access(parent_dir, os.W_OK)
    except Exception:
        return False