"""资源文件验证器

验证图标、音效等资源文件是否存在。
"""

from typing import Dict, Any, Tuple, List
from pathlib import Path
import os


def validate_field(field_name: str, value: Any, params: Dict[str, Any], row_data: Dict[str, Any]) -> Tuple[bool, str]:
    """验证资源文件字段
    
    参数：
    - type: 资源类型 ('icon', 'sound', 'image')
    - base_path: 资源基础路径（可选，默认当前目录）
    - extensions: 允许的文件扩展名列表（可选）
    """
    
    # 检查是否为空
    if value is None or str(value).strip() == "":
        return False, f"Field '{field_name}' is required"
    
    resource_file = str(value).strip()
    resource_type = params.get('type', 'file')
    base_path = params.get('base_path', '.')
    extensions = params.get('extensions', [])
    
    # 构建完整路径
    full_path = Path(base_path) / resource_file
    
    # 检查文件是否存在
    if not full_path.exists():
        return False, f"Field '{field_name}': Resource file '{resource_file}' not found at '{full_path}'"
    
    # 检查是否为文件
    if not full_path.is_file():
        return False, f"Field '{field_name}': '{resource_file}' is not a file"
    
    # 检查文件扩展名
    if extensions:
        file_ext = full_path.suffix.lower()
        if file_ext not in extensions:
            return False, f"Field '{field_name}': File '{resource_file}' has invalid extension '{file_ext}', allowed: {extensions}"
    
    # 特定资源类型的验证
    if resource_type == 'icon':
        return _validate_icon(field_name, full_path, params)
    elif resource_type == 'sound':
        return _validate_sound(field_name, full_path, params)
    elif resource_type == 'image':
        return _validate_image(field_name, full_path, params)
    
    return True, ""


def _validate_icon(field_name: str, file_path: Path, params: Dict[str, Any]) -> Tuple[bool, str]:
    """验证图标文件"""
    allowed_extensions = ['.png', '.jpg', '.jpeg', '.svg', '.ico']
    
    if file_path.suffix.lower() not in allowed_extensions:
        return False, f"Field '{field_name}': Icon file must have one of these extensions: {allowed_extensions}"
    
    # 检查文件大小（图标不应该太大）
    max_size = params.get('max_size', 1024 * 1024)  # 默认1MB
    if file_path.stat().st_size > max_size:
        return False, f"Field '{field_name}': Icon file is too large (max {max_size} bytes)"
    
    return True, ""


def _validate_sound(field_name: str, file_path: Path, params: Dict[str, Any]) -> Tuple[bool, str]:
    """验证音效文件"""
    allowed_extensions = ['.mp3', '.wav', '.ogg', '.m4a']
    
    if file_path.suffix.lower() not in allowed_extensions:
        return False, f"Field '{field_name}': Sound file must have one of these extensions: {allowed_extensions}"
    
    return True, ""


def _validate_image(field_name: str, file_path: Path, params: Dict[str, Any]) -> Tuple[bool, str]:
    """验证图片文件"""
    allowed_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp']
    
    if file_path.suffix.lower() not in allowed_extensions:
        return False, f"Field '{field_name}': Image file must have one of these extensions: {allowed_extensions}"
    
    return True, ""