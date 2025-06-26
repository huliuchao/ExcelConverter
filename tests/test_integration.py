"""集成测试 - 测试完整的转换流程"""

import pytest
import json
from pathlib import Path
import sys
import tempfile
import shutil

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from excel_converter.config.config_manager import ConfigManager
from excel_converter.core.excel_reader import ExcelReader
from excel_converter.core.data_processor import DataProcessor
from excel_converter.core.data_merger import DataMerger
from excel_converter.core.type_system import TypeSystem
from excel_converter.formatters.json_variants import JsonArrayFormatter, JsonMapFormatter
from excel_converter.formatters.lua_formatter import LuaFormatter
from excel_converter.validators.validator_engine import ValidatorEngine


class TestIntegration:
    """集成测试"""
    
    @pytest.fixture
    def fixtures_dir(self):
        """获取fixtures目录路径"""
        return Path(__file__).parent.parent / "fixtures"
    
    @pytest.fixture
    def temp_output_dir(self):
        """创建临时输出目录"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def config_manager(self, fixtures_dir):
        """配置管理器"""
        config_path = fixtures_dir / "config" / "test_config.toml"
        manager = ConfigManager(config_path)
        manager.load_config()
        return manager
    
    def test_full_conversion_pipeline_json_array(self, fixtures_dir, config_manager, temp_output_dir):
        """测试完整的转换流程 - JSON数组格式"""
        
        # 1. 初始化组件
        excel_reader = ExcelReader()
        type_system = TypeSystem(config_manager.object_schemas)
        data_merger = DataMerger()
        data_processor = DataProcessor(type_system)
        validator_engine = ValidatorEngine(fixtures_dir / "validators")
        formatter = JsonArrayFormatter()
        
        # 2. 获取导出配置
        export_config = config_manager.get_export_config("test_items")
        assert export_config is not None
        
        # 3. 读取Excel数据
        excel_data_list = []
        for source in export_config.sources:
            excel_file_path = fixtures_dir / "excel" / source.file
            excel_data = excel_reader.read_excel(excel_file_path, source.sheet)
            excel_data_list.append(excel_data)
        
        # 4. 处理数据（单数据源）
        if len(excel_data_list) == 1:
            processed_data = data_processor.process_data(excel_data_list[0], export_config)
        else:
            # 多数据源，先合并再处理
            merged_data = data_merger.merge_data_sources(excel_data_list, export_config)
            processed_data = merged_data
        
        # 6. 数据验证
        validation_errors = validator_engine.validate_data(processed_data, export_config)
        assert len(validation_errors) == 0, f"Validation errors: {validation_errors}"
        
        # 7. 格式化输出
        formatted_output = formatter.format_data(processed_data, "test_items")
        
        # 8. 验证输出格式
        parsed_output = json.loads(formatted_output)
        assert isinstance(parsed_output, list)
        assert len(parsed_output) == 3
        
        # 验证数据内容
        item_ids = [item["ID"] for item in parsed_output]
        assert 1001 in item_ids
        assert 1002 in item_ids
        assert 1003 in item_ids
        
        # 验证属性对象解析
        for item in parsed_output:
            if item["ID"] == 1001:
                assert item["Name"] == "测试剑"
                assert item["Attributes"]["Attack"] == 100
                assert item["Attributes"]["Defense"] == 50
        
        # 9. 保存并验证文件
        output_file = temp_output_dir / "test_items.json"
        formatter.save_to_file(formatted_output, output_file)
        assert output_file.exists()
        
        # 验证保存的文件内容
        with open(output_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        assert saved_data == parsed_output
    
    def test_full_conversion_pipeline_json_map(self, fixtures_dir, config_manager, temp_output_dir):
        """测试完整的转换流程 - JSON映射格式"""
        
        # 使用相同的流程，但使用不同的格式化器
        excel_reader = ExcelReader()
        type_system = TypeSystem(config_manager.object_schemas)
        data_merger = DataMerger()
        data_processor = DataProcessor(type_system)
        formatter = JsonMapFormatter()
        
        export_config = config_manager.get_export_config("test_items")
        
        # 读取和处理数据
        excel_data_list = []
        for source in export_config.sources:
            excel_file_path = fixtures_dir / "excel" / source.file
            excel_data = excel_reader.read_excel(excel_file_path, source.sheet)
            excel_data_list.append(excel_data)
        
        if len(excel_data_list) == 1:
            processed_data = data_processor.process_data(excel_data_list[0], export_config)
        else:
            merged_data = data_merger.merge_data_sources(excel_data_list, export_config)
            processed_data = merged_data
        
        # 格式化为映射格式
        formatted_output = formatter.format_data(processed_data, "test_items")
        
        # 验证输出格式
        parsed_output = json.loads(formatted_output)
        assert isinstance(parsed_output, dict)
        assert "1001" in parsed_output
        assert "1002" in parsed_output
        assert "1003" in parsed_output
        
        # 验证数据内容
        assert parsed_output["1001"]["Name"] == "测试剑"
        assert parsed_output["1001"]["Attributes"]["Attack"] == 100
    
    def test_full_conversion_pipeline_lua(self, fixtures_dir, config_manager, temp_output_dir):
        """测试完整的转换流程 - Lua格式"""
        
        # 使用Lua格式化器
        excel_reader = ExcelReader()
        type_system = TypeSystem(config_manager.object_schemas)
        data_merger = DataMerger()
        data_processor = DataProcessor(type_system)
        formatter = LuaFormatter()
        
        export_config = config_manager.get_export_config("test_items")
        
        # 读取和处理数据
        excel_data_list = []
        for source in export_config.sources:
            excel_file_path = fixtures_dir / "excel" / source.file
            excel_data = excel_reader.read_excel(excel_file_path, source.sheet)
            excel_data_list.append(excel_data)
        
        if len(excel_data_list) == 1:
            processed_data = data_processor.process_data(excel_data_list[0], export_config)
        else:
            merged_data = data_merger.merge_data_sources(excel_data_list, export_config)
            processed_data = merged_data
        
        # 格式化为Lua格式
        formatted_output = formatter.format_data(processed_data, "test_items")
        
        # 验证输出包含预期内容
        assert "return {" in formatted_output
        assert "[1001] =" in formatted_output
        assert 'Name = "测试剑"' in formatted_output
        assert "Attack = 100" in formatted_output
        assert "Defense = 50" in formatted_output
        
        # 保存文件
        output_file = temp_output_dir / "test_items.lua"
        formatter.save_to_file(formatted_output, output_file)
        assert output_file.exists()
    
    def test_multi_sheet_conversion(self, fixtures_dir, temp_output_dir):
        """测试多Sheet转换"""
        
        # 创建多Sheet配置
        multi_sheet_config_content = '''
[input]
source_dir = "./fixtures/excel"
output_dir = "./fixtures/output"

[output]
format = "json_array"

[defaults]
primary_key = "ID"
separator = ","

[exports.multi_items]
sources = [
    { file = "multi_sheet.xlsx", sheet = "weapons" },
    { file = "multi_sheet.xlsx", sheet = "armors" }
]
scope = "sc"
fields = [
    { name = "ID", scope = "sc" },
    { name = "Name", scope = "sc" },
    { name = "Type", scope = "sc" }
]
validators = []
'''
        
        # 创建临时配置文件
        temp_config = temp_output_dir / "multi_config.toml"
        with open(temp_config, 'w', encoding='utf-8') as f:
            f.write(multi_sheet_config_content)
        
        # 加载配置
        config_manager = ConfigManager(temp_config)
        config_manager.load_config()
        
        # 执行转换
        excel_reader = ExcelReader()
        type_system = TypeSystem(config_manager.object_schemas)
        data_merger = DataMerger()
        data_processor = DataProcessor(type_system)
        formatter = JsonArrayFormatter()
        
        export_config = config_manager.get_export_config("multi_items")
        
        # 读取多个Sheet
        excel_data_list = []
        for source in export_config.sources:
            excel_file_path = fixtures_dir / "excel" / source.file
            excel_data = excel_reader.read_excel(excel_file_path, source.sheet)
            excel_data_list.append(excel_data)
        
        # 合并多个数据源
        merged_data = data_merger.merge_data_sources(excel_data_list, export_config)
        processed_data = merged_data
        
        # 验证合并结果
        assert len(processed_data) == 4  # 2个武器 + 2个护甲
        
        # 验证数据来自不同Sheet
        all_items = list(processed_data.values())
        types = [item["Type"] for item in all_items]
        assert "sword" in types
        assert "axe" in types
        assert "helmet" in types
        assert "armor" in types
    
    def test_validation_error_handling(self, fixtures_dir, config_manager):
        """测试验证错误处理"""
        
        # 创建包含错误的数据
        invalid_config_content = '''
[input]
source_dir = "./fixtures/excel"

[output]
format = "json_array"

[defaults]
primary_key = "ID"

[exports.test_items]
sources = [
    { file = "test_items.xlsx", sheet = "Sheet1" }
]
scope = "sc"
fields = [
    { name = "ID", scope = "sc" },
    { name = "Name", scope = "sc" }
]
validators = [
    { field = "ID", script = "test_validator.py", params = { min_value = 2000, max_value = 3000 } }
]
'''
        
        # 创建临时配置（ID范围2000-3000，但测试数据是1001-1003）
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False, encoding='utf-8') as f:
            f.write(invalid_config_content)
            temp_config_path = Path(f.name)
        
        try:
            config_manager = ConfigManager(temp_config_path)
            config_manager.load_config()
            
            # 执行转换（应该产生验证错误）
            excel_reader = ExcelReader()
            type_system = TypeSystem(config_manager.object_schemas)
            data_merger = DataMerger()
            data_processor = DataProcessor(type_system)
            validator_engine = ValidatorEngine(fixtures_dir / "validators")
            
            export_config = config_manager.get_export_config("test_items")
            
            excel_data_list = []
            for source in export_config.sources:
                excel_file_path = fixtures_dir / "excel" / source.file
                excel_data = excel_reader.read_excel(excel_file_path, source.sheet)
                excel_data_list.append(excel_data)
            
            merged_data = data_merger.merge_data_sources(excel_data_list, export_config)
            processed_data = merged_data
            
            # 验证应该产生错误
            validation_errors = validator_engine.validate_data(processed_data, export_config)
            assert len(validation_errors) > 0
            
            # 检查错误信息
            error_text = " ".join(validation_errors)
            assert "out of range" in error_text
            
        finally:
            # 清理临时文件
            temp_config_path.unlink(missing_ok=True)
    
    def test_compare_with_expected_output(self, fixtures_dir, config_manager):
        """测试与期望输出的比较"""
        
        # 执行完整转换
        excel_reader = ExcelReader()
        type_system = TypeSystem(config_manager.object_schemas)
        data_merger = DataMerger()
        data_processor = DataProcessor(type_system)
        formatter = JsonArrayFormatter()
        
        export_config = config_manager.get_export_config("test_items")
        
        excel_data_list = []
        for source in export_config.sources:
            excel_file_path = fixtures_dir / "excel" / source.file
            excel_data = excel_reader.read_excel(excel_file_path, source.sheet)
            excel_data_list.append(excel_data)
        
        if len(excel_data_list) == 1:
            processed_data = data_processor.process_data(excel_data_list[0], export_config)
        else:
            merged_data = data_merger.merge_data_sources(excel_data_list, export_config)
            processed_data = merged_data
        formatted_output = formatter.format_data(processed_data, "test_items")
        
        # 加载期望输出
        expected_file = fixtures_dir / "expected_output" / "test_items.json"
        with open(expected_file, 'r', encoding='utf-8') as f:
            expected_output = json.load(f)
        
        # 比较实际输出与期望输出
        actual_output = json.loads(formatted_output)
        
        # 排序以确保比较的一致性
        actual_sorted = sorted(actual_output, key=lambda x: x["ID"])
        expected_sorted = sorted(expected_output, key=lambda x: x["ID"])
        
        assert actual_sorted == expected_sorted