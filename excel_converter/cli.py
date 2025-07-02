"""命令行接口

提供Excel数据转换器的命令行功能。
"""

import click
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import time
from datetime import datetime

from .config import ConfigManager, ConfigValidator
from .core import ExcelReader, TypeSystem, DataMerger, DataProcessor
from .formatters import LuaFormatter, JsonMapFormatter, JsonArrayFormatter, JsonPackedFormatter
from .utils import ConversionLogger, ConversionError, ProgressLogger
from .utils.file_utils import ensure_directory
from . import __version__


def _setup_context(ctx, config: str, verbose: bool, log_file: Optional[str]) -> None:
    """设置上下文对象（统一的全局选项处理）"""
    ctx.ensure_object(dict)
    
    if 'config_path' not in ctx.obj:
        ctx.obj['config_path'] = Path(config)
        ctx.obj['log_file'] = Path(log_file) if log_file else None
        ctx.obj['verbose'] = verbose
    else:
        if verbose and not ctx.obj.get('verbose', False):
            ctx.obj['verbose'] = verbose
    
    log_level = 'DEBUG' if ctx.obj.get('verbose', False) else 'INFO'
    ctx.obj['logger'] = ConversionLogger(
        log_file=ctx.obj['log_file'],
        level=getattr(__import__('logging'), log_level),
        console_output=True
    )


def common_options(f):
    """添加常用的全局选项到子命令"""
    f = click.option('--config', '-c', type=click.Path(), default='config.toml', 
                     help='Configuration file path')(f)
    f = click.option('--verbose', '-v', is_flag=True, 
                     help='Enable verbose output')(f)
    f = click.option('--log-file', type=click.Path(), 
                     help='Log file path')(f)
    return f


@click.group(invoke_without_command=True)
@click.option('--config', '-c', type=click.Path(), default='config.toml', help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--log-file', type=click.Path(), help='Log file path')
@click.option('--version', '-V', is_flag=True, help='Show version and exit')
@click.pass_context
def cli(ctx, config: str, verbose: bool, log_file: Optional[str], version: bool):
    """Excel数据转换器命令行工具
    
    将Excel文件转换为Lua、JSON等格式的数据文件。
    支持复杂的数据类型、多数据源合并和灵活的验证系统。
    """
    if version:
        click.echo(f"Excel Converter v{__version__}")
        click.echo(f"Python-based Excel data converter for game development")
        ctx.exit(0)
    
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit(0)
    
    _setup_context(ctx, config, verbose, log_file)


@cli.command()
@common_options
@click.option('--export', '-e', help='Specific export to convert (convert all if not specified)')
@click.option('--format', '-f', type=click.Choice(['lua', 'json_map', 'json_array', 'json_packed']), help='Output format (use config default if not specified)')
@click.option('--compact', is_flag=True, help='Use compact format (no indentation)')
@click.option('--scope', '-s', type=click.Choice(['s', 'c', 'sc']), help='Export scope (override config scope)')
@click.option('--output-dir', '-o', type=click.Path(), help='Output directory (default from config)')
@click.option('--excel-dir', type=click.Path(), help='Excel files directory (default from config)')
@click.option('--validators-dir', type=click.Path(), default='validators', help='Validators directory')
@click.option('--validation-report', type=click.Path(), help='Save validation results to file')
@click.option('--dry-run', is_flag=True, help='Perform a dry run without generating files')
@click.pass_context
def convert(ctx, config: str, verbose: bool, log_file: Optional[str], export: Optional[str], 
           format: Optional[str], compact: bool, scope: Optional[str], 
           output_dir: Optional[str], excel_dir: Optional[str], validators_dir: str, 
           validation_report: Optional[str], dry_run: bool):
    """转换Excel数据到指定格式"""
    
    _setup_context(ctx, config, verbose, log_file)
    
    logger = ctx.obj['logger']
    config_path = ctx.obj['config_path']
    
    try:
        if not config_path.exists():
            logger.log_error(f"Configuration file not found: {config_path}")
            logger.log_error("Please ensure the config file exists or specify a valid path with --config")
            sys.exit(1)
        
        logger.log_info("Loading configuration...")
        logger.log_debug(f"Config file path: {config_path}")
        config_manager = ConfigManager(config_path)
        config_manager.load_config()
        logger.log_debug(f"Configuration loaded successfully")
        
        actual_excel_dir = excel_dir if excel_dir else config_manager.input_config.source_dir
        actual_output_dir = output_dir if output_dir else config_manager.input_config.output_dir
        actual_format = format if format else config_manager.output_config.format
        
        logger.log_debug(f"Resolved paths - Excel: {actual_excel_dir}, Output: {actual_output_dir}, Format: {actual_format}")
        
        output_path = Path(actual_output_dir)
        excel_path = Path(actual_excel_dir)
        validators_path = Path(validators_dir)
        
        if not dry_run:
            ensure_directory(output_path)
        
        logger.log_info("Validating configuration...")
        logger.log_debug(f"Found {len(config_manager.exports)} export configurations")
        validator = ConfigValidator()
        config_errors = config_manager.validate_config()
        if config_errors:
            logger.log_validation_error(config_errors)
            sys.exit(1)
        logger.log_debug("Configuration validation passed")
        
        file_errors = validator.validate_file_dependencies(config_manager.exports, excel_path)
        if file_errors:
            logger.log_validation_error(file_errors)
            sys.exit(1)
        
        if export:
            if export not in config_manager.exports:
                logger.log_error(f"Export '{export}' not found in configuration")
                sys.exit(1)
            exports_to_process = {export: config_manager.exports[export]}
        else:
            exports_to_process = config_manager.exports
        
        excel_reader = ExcelReader()
        type_system = TypeSystem(config_manager.object_schemas)
        data_merger = DataMerger()
        data_processor = DataProcessor(type_system)
        
        from .validators import ValidatorEngine
        validator_engine = ValidatorEngine(validators_path)
        
        all_validation_results = {}
        has_validation_errors = False
        
        formatters = {
            'lua': LuaFormatter(compact=compact),
            'json_map': JsonMapFormatter(compact=compact),
            'json_array': JsonArrayFormatter(compact=compact),
            'json_packed': JsonPackedFormatter(compact=compact)
        }
        
        progress = ProgressLogger(len(exports_to_process), logger)
        
        for export_name, export_config in exports_to_process.items():
            try:
                progress.update_progress(f"Processing export '{export_name}'")
                
                if scope:
                    export_config.scope = scope
                
                logger.log_conversion_start(export_name, [f"{s.file}:{s.sheet}" for s in export_config.sources])
                
                excel_data_list = []
                for source in export_config.sources:
                    excel_file_path = excel_path / source.file
                    excel_data = excel_reader.read_excel(excel_file_path, source.sheet)
                    
                    logger.log_file_processing(
                        str(excel_file_path), 
                        source.sheet, 
                        len(excel_data.rows)
                    )
                    
                    excel_data_list.append(excel_data)
                
                if len(excel_data_list) == 1:
                    data_dict = data_processor.process_data(excel_data_list[0], export_config)
                else:
                    logger.log_info(f"Merging {len(excel_data_list)} data sources...")
                    
                    schema_errors = data_merger.validate_schema_with_config_types(excel_data_list, export_config)
                    if schema_errors:
                        for error in schema_errors:
                            logger.log_warning(f"Schema validation: {error}")
                    
                    merge_stats = data_merger.get_merge_statistics(excel_data_list)
                    logger.log_info(f"Merge statistics: {merge_stats['total_sources']} sources, "
                                  f"{merge_stats['total_rows']} total rows, "
                                  f"{merge_stats['unique_fields']} unique fields")
                    
                    merged_data = data_merger.merge_data_sources(excel_data_list, export_config)
                    logger.log_info(f"Successfully merged data: {len(merged_data)} unique records")
                    
                    # 处理合并后的数据（需要将合并后的数据转换为ExcelData格式）
                    # 这里我们创建一个虚拟的ExcelData来复用DataProcessor
                    if excel_data_list:
                        base_excel_data = excel_data_list[0]
                        merged_rows = list(merged_data.values())
                        
                        from .core.excel_reader import ExcelData
                        virtual_excel_data = ExcelData(
                            file_path=base_excel_data.file_path,
                            sheet_name="merged",
                            fields=base_excel_data.fields,
                            rows=merged_rows
                        )
                        
                        data_dict = data_processor.process_data(virtual_excel_data, export_config)
                    else:
                        data_dict = merged_data
                
                # 数据验证
                validation_errors = []
                if export_config.validators:
                    logger.log_info(f"Validating data with {len(export_config.validators)} validators...")
                    validation_errors = validator_engine.validate_data(data_dict, export_config)
                    
                    validation_result = {
                        'export_name': export_name,
                        'total_records': len(data_dict),
                        'total_errors': len(validation_errors),
                        'errors': validation_errors,
                        'validators_count': len(export_config.validators),
                        'data_sources': [f"{s.file}:{s.sheet}" for s in export_config.sources]
                    }
                    all_validation_results[export_name] = validation_result
                    
                    if validation_errors:
                        has_validation_errors = True
                        logger.log_error(f"Data validation failed for export '{export_name}':")
                        for error in validation_errors:
                            logger.log_error(f"  - {error}")
                        
                        if config_manager.get_default('stop_on_validation_error', True):
                            sys.exit(1)
                        else:
                            logger.log_warning("Continuing despite validation errors...")
                    else:
                        logger.log_info("Data validation passed")
                else:
                    validation_result = {
                        'export_name': export_name,
                        'total_records': len(data_dict),
                        'total_errors': 0,
                        'errors': [],
                        'validators_count': 0,
                        'data_sources': [f"{s.file}:{s.sheet}" for s in export_config.sources]
                    }
                    all_validation_results[export_name] = validation_result
                
                output_format = actual_format
                formatter = formatters.get(output_format)
                
                if output_format == 'json_packed' and formatter:
                    formatter = JsonPackedFormatter(compact=compact, primary_key=export_config.primary_key)
                
                if not formatter:
                    logger.log_error(f"Unsupported output format: {output_format}")
                    logger.log_error(f"Supported formats: {', '.join(formatters.keys())}")
                    sys.exit(1)
                
                logger.log_debug(f"Formatting {len(data_dict)} records with {output_format} formatter")
                formatted_data = formatter.format_data(data_dict, export_name)
                
                if not dry_run:
                    output_filename = formatter.get_output_filename(export_name)
                    output_file_path = output_path / output_filename
                    formatter.save_to_file(formatted_data, output_file_path)
                    
                    logger.log_conversion_complete(export_name, [str(output_file_path)])
                else:
                    logger.log_info(f"Dry run: would generate {formatter.get_output_filename(export_name)}")
                
            except Exception as e:
                logger.log_error(f"Failed to process export '{export_name}'", e)
                if not ctx.obj.get('continue_on_error', False):
                    sys.exit(1)
        
        progress.log_completion()
        
        # 生成验证报告
        if validation_report and all_validation_results:
            _save_validation_report(all_validation_results, Path(validation_report))
            logger.log_info(f"Validation report saved to: {validation_report}")
        
        if has_validation_errors:
            total_errors = sum(r['total_errors'] for r in all_validation_results.values())
            logger.log_warning(f"All conversions completed with {total_errors} validation errors!")
            logger.log_warning("Please review the validation report for details.")
        else:
            logger.log_info("All conversions completed successfully!")
        
    except Exception as e:
        logger.log_error("Conversion failed", e)
        sys.exit(1)


@cli.command()
@common_options
@click.pass_context
def validate_config(ctx, config: str, verbose: bool, log_file: Optional[str]):
    """验证配置文件"""
    _setup_context(ctx, config, verbose, log_file)
    
    logger = ctx.obj['logger']
    config_path = ctx.obj['config_path']
    
    try:
        if not config_path.exists():
            logger.log_error(f"Configuration file not found: {config_path}")
            logger.log_error("Please ensure the config file exists or specify a valid path with --config")
            sys.exit(1)
        
        logger.log_info("Validating configuration file...")
        
        validator = ConfigValidator()
        
        syntax_errors = validator.validate_toml_syntax(config_path)
        if syntax_errors:
            logger.log_validation_error(syntax_errors)
            sys.exit(1)
        
        config_manager = ConfigManager(config_path)
        config_manager.load_config()
        
        config_errors = config_manager.validate_config()
        if config_errors:
            logger.log_validation_error(config_errors)
            sys.exit(1)
        
        schema_errors = validator.validate_object_schemas(config_manager.object_schemas)
        if schema_errors:
            logger.log_validation_error(schema_errors)
            sys.exit(1)
        
        logger.log_info("Configuration file is valid!")
        
    except Exception as e:
        logger.log_error("Configuration validation failed", e)
        sys.exit(1)


@cli.command()
@common_options
@click.pass_context
def list_exports(ctx, config: str, verbose: bool, log_file: Optional[str]):
    """列出所有导出配置"""
    _setup_context(ctx, config, verbose, log_file)
    
    logger = ctx.obj['logger']
    config_path = ctx.obj['config_path']
    
    try:
        if not config_path.exists():
            logger.log_error(f"Configuration file not found: {config_path}")
            logger.log_error("Please ensure the config file exists or specify a valid path with --config")
            sys.exit(1)
        
        config_manager = ConfigManager(config_path)
        config_manager.load_config()
        
        exports = config_manager.list_exports()
        
        if not exports:
            logger.log_info("No exports configured.")
            return
        
        logger.log_info("Available exports:")
        for export_name in exports:
            export_config = config_manager.get_export_config(export_name)
            sources_info = [f"{s.file}:{s.sheet}" for s in export_config.sources]
            logger.log_info(f"  {export_name} (scope: {export_config.scope}, sources: {', '.join(sources_info)})")
        
    except Exception as e:
        logger.log_error("Failed to list exports", e)
        sys.exit(1)


@cli.command()
@common_options
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--sheet', help='Sheet name to preview (first sheet if not specified)')
@click.pass_context
def preview(ctx, config: str, verbose: bool, log_file: Optional[str], file_path: str, sheet: Optional[str]):
    """预览Excel文件结构"""
    _setup_context(ctx, config, verbose, log_file)
    
    logger = ctx.obj['logger']
    
    try:
        excel_reader = ExcelReader()
        file_path = Path(file_path)
        
        sheet_names = excel_reader.get_sheet_names(file_path)
        logger.log_info(f"Available sheets: {', '.join(sheet_names)}")
        
        target_sheet = sheet or sheet_names[0]
        
        preview_info = excel_reader.get_field_preview(file_path, target_sheet)
        
        logger.log_info(f"Preview of sheet '{target_sheet}':")
        logger.log_info(f"Total rows: {preview_info['total_rows']}")
        logger.log_info("Fields:")
        for field in preview_info['fields']:
            logger.log_info(f"  {field['name']} ({field['type']})")
        
        if preview_info['preview_rows']:
            logger.log_info("Sample data:")
            for i, row in enumerate(preview_info['preview_rows'], 1):
                logger.log_info(f"  Row {i}: {row}")
        
    except Exception as e:
        logger.log_error("Failed to preview Excel file", e)
        sys.exit(1)


def _save_validation_report(results: Dict[str, Any], output_path: Path):
    """保存验证报告到文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=== EXCEL CONVERTER VALIDATION REPORT ===\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        total_exports = len(results)
        total_records = sum(r['total_records'] for r in results.values())
        total_errors = sum(r['total_errors'] for r in results.values())
        exports_with_validators = sum(1 for r in results.values() if r['validators_count'] > 0)
        exports_with_errors = sum(1 for r in results.values() if r['total_errors'] > 0)
        
        f.write(f"SUMMARY:\n")
        f.write(f"  Total exports processed: {total_exports}\n")
        f.write(f"  Exports with validators: {exports_with_validators}\n")
        f.write(f"  Exports with errors: {exports_with_errors}\n")
        f.write(f"  Total records processed: {total_records}\n")
        f.write(f"  Total validation errors: {total_errors}\n\n")
        
        for export_name, result in results.items():
            f.write(f"{'='*60}\n")
            f.write(f"Export: {export_name}\n")
            f.write(f"Data Sources: {', '.join(result['data_sources'])}\n")
            f.write(f"Records Processed: {result['total_records']}\n")
            f.write(f"Validators Applied: {result['validators_count']}\n")
            f.write(f"Validation Errors: {result['total_errors']}\n")
            f.write(f"{'='*60}\n\n")
            
            if result['total_errors'] > 0:
                f.write("VALIDATION ERRORS:\n")
                for i, error in enumerate(result['errors'], 1):
                    f.write(f"{i:3d}. {error}\n")
                f.write("\n")
            elif result['validators_count'] > 0:
                f.write("✓ All validation checks passed!\n\n")
            else:
                f.write("ℹ No validators configured for this export.\n\n")


if __name__ == '__main__':
    cli()