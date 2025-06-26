"""验证器引擎测试"""

import pytest
from pathlib import Path
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from excel_converter.validators.validator_engine import ValidatorEngine
from excel_converter.config.config_manager import ConfigManager, ValidatorConfig


class TestValidatorEngine:
    """验证器引擎测试"""
    
    @pytest.fixture
    def fixtures_dir(self):
        """获取fixtures目录路径"""
        return Path(__file__).parent.parent / "fixtures"
    
    @pytest.fixture
    def validator_engine(self, fixtures_dir):
        """创建验证器引擎实例"""
        validators_dir = fixtures_dir / "validators"
        return ValidatorEngine(validators_dir)
    
    @pytest.fixture
    def test_data(self):
        """测试数据"""
        return {
            "1001": {
                "ID": 1001,
                "Name": "测试剑",
                "Attributes": {"Attack": 100, "Defense": 50}
            },
            "1002": {
                "ID": 1002,
                "Name": "测试盾",
                "Attributes": {"Attack": 10, "Defense": 200}
            }
        }
    
    @pytest.fixture
    def test_export_config(self):
        """测试导出配置"""
        from excel_converter.config.config_manager import ExportConfig, SourceConfig, FieldConfig
        
        return ExportConfig(
            sources=[SourceConfig(file="test_items.xlsx", sheet="Sheet1")],
            scope="sc",
            primary_key="ID",
            fields=[
                FieldConfig(name="ID", scope="sc"),
                FieldConfig(name="Name", scope="sc"),
                FieldConfig(name="Attributes", scope="sc")
            ],
            validators=[
                ValidatorConfig(field="ID", script="test_validator.py", params={"min_value": 1000, "max_value": 2000}),
                ValidatorConfig(field="Name", script="test_validator.py")
            ]
        )
    
    def test_load_valid_validator(self, validator_engine):
        """测试加载有效验证器"""
        module = validator_engine._load_validator_script("test_validator.py")
        
        # 检查必需的函数是否存在
        assert hasattr(module, 'validate_field')
        assert hasattr(module, 'validate_row')
        assert hasattr(module, 'validate_dataset')
        
        # 检查函数是否可调用
        assert callable(module.validate_field)
        assert callable(module.validate_row)
        assert callable(module.validate_dataset)
    
    def test_load_nonexistent_validator(self, validator_engine):
        """测试加载不存在的验证器"""
        with pytest.raises(Exception):
            validator_engine._load_validator_script("nonexistent_validator.py")
    
    def test_validate_field_success(self, validator_engine, test_export_config):
        """测试字段验证成功"""
        row_data = {"ID": 1001, "Name": "测试剑"}
        
        # 测试ID验证
        errors = validator_engine._validate_field(
            "ID", 1001, 
            test_export_config.validators[0], 
            row_data, 
            "1001"
        )
        assert len(errors) == 0
        
        # 测试Name验证
        errors = validator_engine._validate_field(
            "Name", "测试剑", 
            test_export_config.validators[1], 
            row_data, 
            "1001"
        )
        assert len(errors) == 0
    
    def test_validate_field_failure(self, validator_engine, test_export_config):
        """测试字段验证失败"""
        row_data = {"ID": -1, "Name": ""}
        
        # 测试无效ID
        errors = validator_engine._validate_field(
            "ID", -1, 
            test_export_config.validators[0], 
            row_data, 
            "1001"
        )
        assert len(errors) > 0
        assert "positive integer" in errors[0]
        
        # 测试空名称
        errors = validator_engine._validate_field(
            "Name", "", 
            test_export_config.validators[1], 
            row_data, 
            "1001"
        )
        assert len(errors) > 0
        assert "cannot be empty" in errors[0]
    
    def test_validate_data_success(self, validator_engine, test_data, test_export_config):
        """测试完整数据验证成功"""
        errors = validator_engine.validate_data(test_data, test_export_config)
        assert len(errors) == 0
    
    def test_validate_data_with_errors(self, validator_engine, test_export_config):
        """测试包含错误的数据验证"""
        invalid_data = {
            "1001": {
                "ID": -1,  # 无效ID
                "Name": "",  # 空名称
                "Attributes": {"Attack": 100, "Defense": 50}
            }
        }
        
        errors = validator_engine.validate_data(invalid_data, test_export_config)
        assert len(errors) > 0
        
        # 检查错误信息
        error_text = " ".join(errors)
        assert "positive integer" in error_text
        assert "cannot be empty" in error_text
    
    def test_validate_broken_validator(self, fixtures_dir):
        """测试故意损坏的验证器"""
        validators_dir = fixtures_dir / "validators"
        validator_engine = ValidatorEngine(validators_dir)
        
        # 创建使用损坏验证器的配置
        broken_config = ValidatorConfig(field="ID", script="broken_validator.py")
        
        # 验证应该捕获异常并返回错误
        errors = validator_engine._validate_field(
            "ID", 1001, 
            broken_config, 
            {"ID": 1001}, 
            "1001"
        )
        assert len(errors) > 0
        assert "test error" in errors[0] or "exception" in errors[0].lower()
    
    def test_validator_interface_validation(self, validator_engine):
        """测试验证器接口验证"""
        # 测试有效验证器
        errors = validator_engine.validate_validator_interface("test_validator.py")
        assert len(errors) == 0
        
        # 测试损坏的验证器
        errors = validator_engine.validate_validator_interface("broken_validator.py")
        assert len(errors) > 0
        
        # 检查是否检测到接口问题
        error_text = " ".join(errors)
        assert "signature" in error_text or "interface" in error_text
    
    def test_validate_row(self, validator_engine, test_export_config):
        """测试行级验证"""
        # 正确的数据
        correct_row = {"ID": 1001, "Name": "测试剑"}
        errors = validator_engine._validate_row(correct_row, test_export_config, "1001")
        assert len(errors) == 0
        
        # 错误的数据（违反业务规则）
        incorrect_row = {"ID": 1001, "Name": "错误名称"}
        errors = validator_engine._validate_row(incorrect_row, test_export_config, "1001")
        assert len(errors) > 0
        assert "测试剑" in errors[0]
    
    def test_validate_dataset(self, validator_engine, test_data, test_export_config):
        """测试数据集级验证"""
        dataset = list(test_data.values())
        errors = validator_engine._validate_dataset(dataset, test_export_config)
        assert len(errors) == 0
        
        # 测试重复ID的情况
        duplicate_data = [
            {"ID": 1001, "Name": "测试剑1"},
            {"ID": 1001, "Name": "测试剑2"}  # 重复ID
        ]
        errors = validator_engine._validate_dataset(duplicate_data, test_export_config)
        assert len(errors) > 0
        assert "Duplicate" in errors[0]
    
    def test_scope_filtering_in_validation(self, validator_engine):
        """测试验证器中的scope过滤功能"""
        from excel_converter.config.config_manager import ExportConfig, SourceConfig, FieldConfig, ValidatorConfig
        
        # 创建测试数据
        test_data = {
            1001: {
                "ID": 1001,
                "Name": "Test Item",
                "ServerConfig": "server_only_data",
                "ClientConfig": "client_only_data"
            }
        }
        
        # 创建包含不同scope字段的导出配置
        export_config = ExportConfig(
            sources=[SourceConfig(file="test.xlsx", sheet="Sheet1")],
            scope="s",  # 只导出服务器端数据
            primary_key="ID",
            fields=[
                FieldConfig(name="ID", scope="sc"),
                FieldConfig(name="Name", scope="sc"),
                FieldConfig(name="ServerConfig", scope="s"),
                FieldConfig(name="ClientConfig", scope="c")
            ],
            validators=[
                ValidatorConfig(field="ID", script="test_validator.py"),
                ValidatorConfig(field="Name", script="test_validator.py"),
                ValidatorConfig(field="ServerConfig", script="test_validator.py"),
                ValidatorConfig(field="ClientConfig", script="test_validator.py")  # 这个不应该被验证
            ]
        )
        
        # 执行验证
        errors = validator_engine.validate_data(test_data, export_config)
        
        # 检查结果：不应该有来自ClientConfig字段的验证错误
        # 因为在scope="s"的情况下，ClientConfig字段不会被导出，所以也不应该被验证
        client_config_errors = [e for e in errors if "ClientConfig" in e]
        assert len(client_config_errors) == 0, f"ClientConfig should not be validated in server scope, but got errors: {client_config_errors}"
    
    def test_scope_filtering_different_scopes(self, validator_engine):
        """测试不同scope下的验证行为"""
        from excel_converter.config.config_manager import ExportConfig, SourceConfig, FieldConfig, ValidatorConfig
        
        # 创建测试数据
        test_data = {
            1001: {
                "ID": 1001,
                "Name": "Test Item",
                "ServerConfig": "server_data",
                "ClientConfig": "client_data"
            }
        }
        
        # 创建字段配置
        fields = [
            FieldConfig(name="ID", scope="sc"),
            FieldConfig(name="Name", scope="sc"),
            FieldConfig(name="ServerConfig", scope="s"),
            FieldConfig(name="ClientConfig", scope="c")
        ]
        
        validators = [
            ValidatorConfig(field="ID", script="test_validator.py"),
            ValidatorConfig(field="ServerConfig", script="test_validator.py"),
            ValidatorConfig(field="ClientConfig", script="test_validator.py")
        ]
        
        # 测试服务器端scope
        server_config = ExportConfig(
            sources=[SourceConfig(file="test.xlsx", sheet="Sheet1")],
            scope="s",
            primary_key="ID",
            fields=fields,
            validators=validators
        )
        
        server_errors = validator_engine.validate_data(test_data, server_config)
        server_client_errors = [e for e in server_errors if "ClientConfig" in e]
        assert len(server_client_errors) == 0, "ClientConfig should not be validated in server scope"
        
        # 测试客户端scope
        client_config = ExportConfig(
            sources=[SourceConfig(file="test.xlsx", sheet="Sheet1")],
            scope="c",
            primary_key="ID",
            fields=fields,
            validators=validators
        )
        
        client_errors = validator_engine.validate_data(test_data, client_config)
        client_server_errors = [e for e in client_errors if "ServerConfig" in e]
        assert len(client_server_errors) == 0, "ServerConfig should not be validated in client scope"