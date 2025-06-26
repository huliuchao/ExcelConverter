"""CLI测试

测试命令行界面的功能。
"""

import pytest
from click.testing import CliRunner
from excel_converter.cli import cli


class TestCLI:
    """测试CLI功能"""
    
    def test_main_help_without_config(self):
        """测试主命令帮助不需要配置文件"""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "Excel数据转换器命令行工具" in result.output
        assert "Commands:" in result.output
        
    def test_convert_help_without_config(self):
        """测试convert子命令帮助不需要配置文件"""
        runner = CliRunner()
        result = runner.invoke(cli, ['convert', '--help'])
        
        assert result.exit_code == 0
        assert "转换Excel数据到指定格式" in result.output
        assert "Options:" in result.output
        # 验证子命令中也包含全局选项
        assert "--config" in result.output
        assert "--verbose" in result.output
        
    def test_list_exports_help_without_config(self):
        """测试list-exports子命令帮助不需要配置文件"""
        runner = CliRunner()
        result = runner.invoke(cli, ['list-exports', '--help'])
        
        assert result.exit_code == 0
        assert "列出所有导出配置" in result.output
        # 验证子命令中也包含全局选项
        assert "--config" in result.output
        assert "--verbose" in result.output
        
    def test_preview_help_without_config(self):
        """测试preview子命令帮助不需要配置文件"""
        runner = CliRunner()
        result = runner.invoke(cli, ['preview', '--help'])
        
        assert result.exit_code == 0
        assert "预览Excel文件结构" in result.output
        # 验证子命令中也包含全局选项
        assert "--config" in result.output
        assert "--verbose" in result.output
        
    def test_validate_config_help_without_config(self):
        """测试validate-config子命令帮助不需要配置文件"""
        runner = CliRunner()
        result = runner.invoke(cli, ['validate-config', '--help'])
        
        assert result.exit_code == 0
        assert "验证配置文件" in result.output
        # 验证子命令中也包含全局选项
        assert "--config" in result.output
        assert "--verbose" in result.output
    
    def test_nonexistent_config_file_error(self):
        """测试配置文件不存在时的错误处理"""
        runner = CliRunner()
        result = runner.invoke(cli, ['--config', 'nonexistent.toml', 'convert'])
        
        assert result.exit_code == 1
        assert "Configuration file not found" in result.output
        assert "nonexistent.toml" in result.output
        
    def test_verbose_option(self):
        """测试verbose选项"""
        runner = CliRunner()
        result = runner.invoke(cli, ['--verbose', '--help'])
        
        assert result.exit_code == 0
        assert "Excel数据转换器命令行工具" in result.output
    
    def test_version_option_long(self):
        """测试--version选项"""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        
        assert result.exit_code == 0
        assert "Excel Converter v0.0.1" in result.output
        assert "Python-based Excel data converter for game development" in result.output
    
    def test_version_option_short(self):
        """测试-V选项"""
        runner = CliRunner()
        result = runner.invoke(cli, ['-V'])
        
        assert result.exit_code == 0
        assert "Excel Converter v0.0.1" in result.output
        assert "Python-based Excel data converter for game development" in result.output
    
    def test_no_command_shows_help(self):
        """测试无命令时显示帮助"""
        runner = CliRunner()
        result = runner.invoke(cli, [])
        
        assert result.exit_code == 0
        assert "Excel数据转换器命令行工具" in result.output
        assert "Commands:" in result.output


class TestFlexibleParameterOrder:
    """测试灵活的参数顺序功能"""
    
    def test_traditional_global_options_before_subcommand(self):
        """测试全局选项在子命令之前"""
        runner = CliRunner()
        
        # 全局选项在子命令之前
        result = runner.invoke(cli, ['--config', 'fixtures/config/test_config.toml', 'convert', '--help'])
        assert result.exit_code == 0
        assert "转换Excel数据到指定格式" in result.output
    
    def test_flexible_global_options_after_subcommand(self):
        """测试全局选项在子命令之后"""
        runner = CliRunner()
        
        # 灵活参数顺序：全局选项可以在子命令之后
        result = runner.invoke(cli, ['convert', '--config', 'fixtures/config/test_config.toml', '--help'])
        assert result.exit_code == 0
        assert "转换Excel数据到指定格式" in result.output
        
    def test_mixed_parameter_order_convert(self):
        """测试混合参数顺序 - convert命令"""
        runner = CliRunner()
        
        # 测试多种参数顺序组合
        test_cases = [
            # 全局选项在前
            ['--config', 'fixtures/config/test_config.toml', 'convert', '--help'],
            # 全局选项在后
            ['convert', '--config', 'fixtures/config/test_config.toml', '--help'],
            # 混合顺序
            ['--verbose', 'convert', '--config', 'fixtures/config/test_config.toml', '--help'],
            # 复杂混合
            ['convert', '--verbose', '--config', 'fixtures/config/test_config.toml', '--help']
        ]
        
        for args in test_cases:
            result = runner.invoke(cli, args)
            assert result.exit_code == 0, f"Failed with args: {args}"
            assert "转换Excel数据到指定格式" in result.output
    
    def test_mixed_parameter_order_list_exports(self):
        """测试混合参数顺序 - list-exports命令"""
        runner = CliRunner()
        
        test_cases = [
            ['--config', 'fixtures/config/test_config.toml', 'list-exports', '--help'],
            ['list-exports', '--config', 'fixtures/config/test_config.toml', '--help'],
            ['--verbose', 'list-exports', '--config', 'fixtures/config/test_config.toml', '--help'],
            ['list-exports', '--verbose', '--config', 'fixtures/config/test_config.toml', '--help']
        ]
        
        for args in test_cases:
            result = runner.invoke(cli, args)
            assert result.exit_code == 0, f"Failed with args: {args}"
            assert "列出所有导出配置" in result.output
    
    def test_mixed_parameter_order_validate_config(self):
        """测试混合参数顺序 - validate-config命令"""
        runner = CliRunner()
        
        test_cases = [
            ['--config', 'fixtures/config/test_config.toml', 'validate-config', '--help'],
            ['validate-config', '--config', 'fixtures/config/test_config.toml', '--help'],
            ['--verbose', 'validate-config', '--config', 'fixtures/config/test_config.toml', '--help'],
            ['validate-config', '--verbose', '--config', 'fixtures/config/test_config.toml', '--help']
        ]
        
        for args in test_cases:
            result = runner.invoke(cli, args)
            assert result.exit_code == 0, f"Failed with args: {args}"
            assert "验证配置文件" in result.output
    
    def test_mixed_parameter_order_preview(self):
        """测试混合参数顺序 - preview命令"""
        runner = CliRunner()
        
        test_cases = [
            ['--verbose', 'preview', 'fixtures/excel/test_items.xlsx', '--help'],
            ['preview', '--verbose', 'fixtures/excel/test_items.xlsx', '--help'],
            ['preview', 'fixtures/excel/test_items.xlsx', '--verbose', '--help']
        ]
        
        for args in test_cases:
            result = runner.invoke(cli, args)
            assert result.exit_code == 0, f"Failed with args: {args}"
            assert "预览Excel文件结构" in result.output
    
    def test_global_options_priority(self):
        """测试全局选项的优先级处理"""
        runner = CliRunner()
        
        # 测试当全局选项既在主命令又在子命令中指定时的行为
        # 这里主要测试不会出错，具体优先级逻辑由_setup_context处理
        result = runner.invoke(cli, [
            '--verbose', 
            'convert', 
            '--config', 'fixtures/config/test_config.toml',
            '--verbose',  # 重复的verbose选项
            '--help'
        ])
        assert result.exit_code == 0
        assert "转换Excel数据到指定格式" in result.output
    
    def test_complex_mixed_options_convert(self):
        """测试复杂的混合选项顺序 - convert命令"""
        runner = CliRunner()
        
        # 测试非常复杂的参数组合
        result = runner.invoke(cli, [
            'convert',
            '--format', 'lua',
            '--verbose',
            '--config', 'fixtures/config/test_config.toml',
            '--export', 'test_export',
            '--dry-run',
            '--help'
        ])
        assert result.exit_code == 0
        assert "转换Excel数据到指定格式" in result.output


class TestCLIUserFriendliness:
    """测试CLI的用户友好性"""
    
    def test_help_suggests_config_path(self):
        """测试帮助信息中提到配置文件路径"""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "--config" in result.output
        assert "Configuration file path" in result.output
    
    def test_convert_help_mentions_config_defaults(self):
        """测试convert帮助提到配置文件默认值"""
        runner = CliRunner()
        result = runner.invoke(cli, ['convert', '--help'])
        
        assert result.exit_code == 0
        assert "default from config" in result.output
    
    def test_config_file_error_message_helpful(self):
        """测试配置文件错误信息有帮助性"""
        runner = CliRunner()
        result = runner.invoke(cli, ['--config', 'missing.toml', 'convert'])
        
        assert result.exit_code == 1
        assert "Configuration file not found" in result.output
        assert "Please ensure the config file exists" in result.output
        assert "--config" in result.output
    
    def test_subcommand_global_options_availability(self):
        """测试子命令中全局选项的可用性"""
        runner = CliRunner()
        
        subcommands = ['convert', 'list-exports', 'validate-config', 'preview']
        
        for subcommand in subcommands:
            if subcommand == 'preview':
                result = runner.invoke(cli, [subcommand, 'fixtures/excel/test_items.xlsx', '--help'])
            else:
                result = runner.invoke(cli, [subcommand, '--help'])
            
            assert result.exit_code == 0, f"Failed for subcommand: {subcommand}"
            assert "--config" in result.output, f"Missing --config in {subcommand}"
            assert "--verbose" in result.output, f"Missing --verbose in {subcommand}"
            assert "--log-file" in result.output, f"Missing --log-file in {subcommand}"
