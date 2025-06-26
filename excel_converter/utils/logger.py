"""日志工具

提供格式化的日志输出功能。
"""

import logging
import sys
from pathlib import Path
from typing import Optional, List
from datetime import datetime


class ConversionLogger:
    """转换过程的日志记录器"""
    
    def __init__(self, log_file: Optional[Path] = None, level: int = logging.INFO, console_output: bool = True):
        self.logger = logging.getLogger('excel_converter')
        self.logger.setLevel(level)
        
        self.logger.handlers.clear()
        
        self._setup_logger(log_file, level, console_output)
    
    def _setup_logger(self, log_file: Optional[Path], level: int, console_output: bool) -> None:
        """设置日志配置"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def log_conversion_start(self, export_name: str, sources: List[str]) -> None:
        """记录转换开始"""
        self.logger.info(f"Starting conversion for export '{export_name}'")
        self.logger.info(f"Data sources: {', '.join(sources)}")
    
    def log_conversion_complete(self, export_name: str, output_files: List[str]) -> None:
        """记录转换完成"""
        self.logger.info(f"Conversion completed for export '{export_name}'")
        self.logger.info(f"Output files: {', '.join(output_files)}")
    
    def log_validation_error(self, errors: List[str]) -> None:
        """记录验证错误"""
        self.logger.error(f"Validation failed with {len(errors)} errors:")
        for i, error in enumerate(errors, 1):
            self.logger.error(f"  {i}. {error}")
    
    def log_file_processing(self, file_path: str, sheet_name: str, row_count: int) -> None:
        """记录文件处理信息"""
        self.logger.info(f"Processing file: {file_path}, sheet: {sheet_name}, rows: {row_count}")
    
    def log_type_conversion(self, field_name: str, original_type: str, target_type: str, count: int) -> None:
        """记录类型转换信息"""
        self.logger.debug(f"Converting field '{field_name}' from {original_type} to {target_type} ({count} values)")
    
    def log_data_merge(self, source_count: int, total_rows: int, merged_rows: int) -> None:
        """记录数据合并信息"""
        self.logger.info(f"Merged {source_count} data sources: {total_rows} total rows -> {merged_rows} unique rows")
    
    def log_scope_filter(self, original_count: int, filtered_count: int, scope: str) -> None:
        """记录作用域过滤信息"""
        self.logger.info(f"Scope filter '{scope}': {original_count} fields -> {filtered_count} fields")
    
    def log_performance(self, operation: str, duration_seconds: float) -> None:
        """记录性能信息"""
        self.logger.info(f"Performance: {operation} took {duration_seconds:.2f} seconds")
    
    def log_warning(self, message: str) -> None:
        """记录警告"""
        self.logger.warning(message)
    
    def log_error(self, message: str, exception: Optional[Exception] = None) -> None:
        """记录错误"""
        if exception:
            self.logger.error(f"{message}: {exception}", exc_info=True)
        else:
            self.logger.error(message)
    
    def log_debug(self, message: str) -> None:
        """记录调试信息"""
        self.logger.debug(message)
    
    def log_info(self, message: str) -> None:
        """记录一般信息"""
        self.logger.info(message)


class ProgressLogger:
    """进度日志记录器"""
    
    def __init__(self, total_steps: int, logger: Optional[ConversionLogger] = None):
        self.total_steps = total_steps
        self.current_step = 0
        self.logger = logger
        self.start_time = datetime.now()
    
    def update_progress(self, step_name: str, details: str = "") -> None:
        """更新进度"""
        self.current_step += 1
        progress = (self.current_step / self.total_steps) * 100
        
        message = f"[{progress:.1f}%] {step_name}"
        if details:
            message += f" - {details}"
        
        if self.logger:
            self.logger.log_info(message)
        else:
            print(message)
    
    def log_completion(self) -> None:
        """记录完成信息"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        message = f"Process completed in {duration:.2f} seconds"
        if self.logger:
            self.logger.log_info(message)
        else:
            print(message)