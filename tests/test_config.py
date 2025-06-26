"""配置管理模块测试"""

import pytest
from pathlib import Path
import sys
import os

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from excel_converter.config.config_manager import ConfigManager
from excel_converter.config.validator import ConfigValidator


class TestConfigManager:
    """配置管理器测试"""
    
    @pytest.fixture
    def fixtures_dir(self):
        """获取fixtures目录路径"""
        return Path(__file__).parent.parent / "fixtures"
    
    @pytest.fixture
    def valid_config_path(self, fixtures_dir):
        """有效配置文件路径"""
        return fixtures_dir / "config" / "test_config.toml"
    
    @pytest.fixture
    def invalid_config_path(self, fixtures_dir):
        """无效配置文件路径"""
        return fixtures_dir / "config" / "invalid_config.toml"
    
    def test_load_valid_config(self, valid_config_path):
        """测试加载有效配置"""
        config_manager = ConfigManager(valid_config_path)
        config_manager.load_config()
        
        # 验证基本配置加载
        assert config_manager.input_config is not None
        assert config_manager.output_config is not None
        assert config_manager.defaults is not None
        
        # 验证导出配置
        assert "test_items" in config_manager.exports
        export_config = config_manager.exports["test_items"]
        
        assert export_config.scope == "sc"
        assert len(export_config.sources) == 1
        assert export_config.sources[0].file == "test_items.xlsx"
        assert export_config.sources[0].sheet == "Sheet1"
        
        # 验证字段配置
        assert len(export_config.fields) == 3
        field_names = [f.name for f in export_config.fields]
        assert "ID" in field_names
        assert "Name" in field_names
        assert "Attributes" in field_names
        
        # 验证验证器配置
        assert len(export_config.validators) == 2
        validator_scripts = [v.script for v in export_config.validators]
        assert "test_validator.py" in validator_scripts
    
    def test_load_nonexistent_config(self):
        """测试加载不存在的配置文件"""
        nonexistent_path = Path("nonexistent_config.toml")
        config_manager = ConfigManager(nonexistent_path)
        
        with pytest.raises(ValueError):
            config_manager.load_config()
    
    def test_validate_valid_config(self, valid_config_path):
        """测试验证有效配置"""
        config_manager = ConfigManager(valid_config_path)
        config_manager.load_config()
        
        errors = config_manager.validate_config()
        assert len(errors) == 0
    
    def test_validate_invalid_config(self, invalid_config_path):
        """测试验证无效配置"""
        config_manager = ConfigManager(invalid_config_path)
        config_manager.load_config()
        
        errors = config_manager.validate_config()
        assert len(errors) > 0
        
        # 检查是否包含预期的错误信息
        error_text = " ".join(errors)
        assert "scope" in error_text or "source" in error_text
    
    def test_get_export_config(self, valid_config_path):
        """测试获取导出配置"""
        config_manager = ConfigManager(valid_config_path)
        config_manager.load_config()
        
        # 存在的导出配置
        export_config = config_manager.get_export_config("test_items")
        assert export_config is not None
        assert export_config.scope == "sc"
        
        # 不存在的导出配置
        nonexistent_config = config_manager.get_export_config("nonexistent")
        assert nonexistent_config is None
    
    def test_resolve_defaults(self, valid_config_path):
        """测试默认值解析"""
        config_manager = ConfigManager(valid_config_path)
        config_manager.load_config()
        
        export_config = config_manager.exports["test_items"]
        
        # 检查默认主键是否被应用
        assert export_config.primary_key == "ID"
        
        # 检查字段默认分隔符是否被应用
        for field in export_config.fields:
            assert field.separator == ","


class TestConfigValidator:
    """配置验证器测试"""
    
    @pytest.fixture
    def fixtures_dir(self):
        """获取fixtures目录路径"""
        return Path(__file__).parent.parent / "fixtures"
    
    def test_validate_toml_syntax(self, fixtures_dir):
        """测试TOML语法验证"""
        validator = ConfigValidator()
        
        # 有效的TOML文件
        valid_config = fixtures_dir / "config" / "test_config.toml"
        errors = validator.validate_toml_syntax(valid_config)
        assert len(errors) == 0
        
        # 测试不存在的文件
        nonexistent_file = fixtures_dir / "config" / "nonexistent.toml"
        errors = validator.validate_toml_syntax(nonexistent_file)
        assert len(errors) > 0
        assert "No such file" in errors[0] or "not found" in errors[0] or "does not exist" in errors[0]