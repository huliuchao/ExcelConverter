"""错误处理工具

定义自定义异常类和错误处理机制。
"""

from typing import List, Any
import traceback


class ConversionError(Exception):
    """转换过程中的错误"""
    pass


class ValidationError(Exception):
    """验证错误"""
    pass


class ConfigurationError(Exception):
    """配置错误"""
    pass


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self, stop_on_error: bool = True):
        self.stop_on_error = stop_on_error
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def handle_error(self, error: Exception, context: str = "") -> None:
        """处理错误"""
        error_msg = f"{context}: {str(error)}" if context else str(error)
        self.errors.append(error_msg)
        
        if self.stop_on_error:
            raise error
    
    def handle_validation_error(self, field_name: str, value: Any, message: str) -> None:
        """处理验证错误"""
        error_msg = f"Validation failed for field '{field_name}' with value '{value}': {message}"
        self.errors.append(error_msg)
        
        if self.stop_on_error:
            raise ValidationError(error_msg)
    
    def handle_warning(self, warning: str, context: str = "") -> None:
        """处理警告"""
        warning_msg = f"{context}: {warning}" if context else warning
        self.warnings.append(warning_msg)
    
    def get_error_summary(self) -> str:
        """获取错误摘要"""
        summary_lines = []
        
        if self.errors:
            summary_lines.append(f"Errors ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                summary_lines.append(f"  {i}. {error}")
        
        if self.warnings:
            if summary_lines:
                summary_lines.append("")
            summary_lines.append(f"Warnings ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                summary_lines.append(f"  {i}. {warning}")
        
        if not summary_lines:
            return "No errors or warnings."
        
        return "\n".join(summary_lines)
    
    def has_errors(self) -> bool:
        """是否有错误"""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """是否有警告"""
        return len(self.warnings) > 0
    
    def clear(self) -> None:
        """清除所有错误和警告"""
        self.errors.clear()
        self.warnings.clear()
    
    def get_exception_details(self, exception: Exception) -> str:
        """获取异常详细信息"""
        return f"{type(exception).__name__}: {str(exception)}\n{traceback.format_exc()}"