"""验证器引擎

负责加载和执行验证器脚本。
"""

from typing import List, Dict, Any, Tuple, Optional
import importlib.util
import sys
from pathlib import Path

from ..config.config_manager import ValidatorConfig, ExportConfig
from ..utils.error_handler import ValidationError
from ..utils.scope_utils import field_matches_scope


class ValidatorEngine:
    """验证器引擎"""
    
    def __init__(self, validator_dir: Path):
        self.validator_dir = validator_dir
        self.loaded_validators = {}
    
    def validate_data(self, data: Dict[str, Any], export_config: ExportConfig) -> List[str]:
        """验证数据"""
        errors = []
        
        if not export_config.validators:
            return errors
        
        dataset = list(data.values())
        
        for row_key, row_data in data.items():
            for validator_config in export_config.validators:
                field_config = self._find_field_config(validator_config.field, export_config.fields)
                
                if field_config and not field_matches_scope(field_config.scope, export_config.scope):
                    continue
                
                field_errors = self._validate_field(
                    validator_config.field, 
                    row_data.get(validator_config.field),
                    validator_config,
                    row_data,
                    row_key
                )
                errors.extend(field_errors)
        
        for row_key, row_data in data.items():
            row_errors = self._validate_row(row_data, export_config, row_key)
            errors.extend(row_errors)
        
        dataset_errors = self._validate_dataset(dataset, export_config)
        errors.extend(dataset_errors)
        
        return errors
    
    def _find_field_config(self, field_name: str, field_configs) -> Optional[Any]:
        """查找字段配置"""
        for field_config in field_configs:
            if field_config.name == field_name:
                return field_config
        return None
    
    def _validate_field(self, field_name: str, value: Any, validator_config: ValidatorConfig, 
                       row_data: Dict[str, Any], row_key: Any) -> List[str]:
        """字段级验证"""
        errors = []
        
        try:
            validator_module = self._load_validator_script(validator_config.script)
            
            if hasattr(validator_module, 'validate_field'):
                params = validator_config.params or {}
                success, message = validator_module.validate_field(
                    field_name, value, params, row_data
                )
                
                if not success:
                    errors.append(f"Row {row_key}: {message}")
            
        except Exception as e:
            errors.append(f"Row {row_key}: Validator error for field '{field_name}': {e}")
        
        return errors
    
    def _validate_row(self, row_data: Dict[str, Any], export_config: ExportConfig, row_key: Any) -> List[str]:
        """行级验证"""
        errors = []
        
        validator_scripts = set()
        for validator_config in export_config.validators:
            validator_scripts.add(validator_config.script)
        
        for script_name in validator_scripts:
            try:
                validator_module = self._load_validator_script(script_name)
                
                if hasattr(validator_module, 'validate_row'):
                    success, message = validator_module.validate_row(
                        row_data, export_config.__dict__
                    )
                    
                    if not success:
                        errors.append(f"Row {row_key}: {message}")
                
            except Exception as e:
                errors.append(f"Row {row_key}: Row validator error in '{script_name}': {e}")
        
        return errors
    
    def _validate_dataset(self, dataset: List[Dict[str, Any]], export_config: ExportConfig) -> List[str]:
        """数据集级验证"""
        errors = []
        
        validator_scripts = set()
        for validator_config in export_config.validators:
            validator_scripts.add(validator_config.script)
        
        for script_name in validator_scripts:
            try:
                validator_module = self._load_validator_script(script_name)
                
                if hasattr(validator_module, 'validate_dataset'):
                    success, message = validator_module.validate_dataset(
                        dataset, export_config.__dict__
                    )
                    
                    if not success:
                        errors.append(f"Dataset validation failed: {message}")
                
            except Exception as e:
                errors.append(f"Dataset validator error in '{script_name}': {e}")
        
        return errors
    
    def _load_validator_script(self, script_name: str) -> Any:
        """动态加载验证器脚本"""
        if script_name in self.loaded_validators:
            return self.loaded_validators[script_name]
        
        script_path = self.validator_dir / script_name
        
        spec = importlib.util.spec_from_file_location(
            f"validator_{script_name.replace('.py', '')}", 
            script_path
        )
        
        if spec is None or spec.loader is None:
            raise ValidationError(f"Failed to load validator script: {script_path}")
        
        module = importlib.util.module_from_spec(spec)
        
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            raise ValidationError(f"Error executing validator script {script_path}: {e}")
        
        self.loaded_validators[script_name] = module
        
        return module
    
    def validate_validator_interface(self, script_name: str) -> List[str]:
        """验证验证器脚本的接口"""
        errors = []
        
        try:
            module = self._load_validator_script(script_name)
            
            if not hasattr(module, 'validate_field'):
                errors.append(f"Validator '{script_name}' missing validate_field function")
            else:
                import inspect
                sig = inspect.signature(module.validate_field)
                params = list(sig.parameters.keys())
                expected_params = ['field_name', 'value', 'params', 'row_data']
                
                if len(params) < 4:
                    errors.append(f"Validator '{script_name}' validate_field function has incorrect signature")
            
            if hasattr(module, 'validate_row'):
                sig = inspect.signature(module.validate_row)
                params = list(sig.parameters.keys())
                if len(params) < 2:
                    errors.append(f"Validator '{script_name}' validate_row function has incorrect signature")
            
            if hasattr(module, 'validate_dataset'):
                sig = inspect.signature(module.validate_dataset)
                params = list(sig.parameters.keys())
                if len(params) < 2:
                    errors.append(f"Validator '{script_name}' validate_dataset function has incorrect signature")
        
        except Exception as e:
            errors.append(f"Error validating validator interface for '{script_name}': {e}")
        
        return errors
    
    def list_available_validators(self) -> List[str]:
        """列出可用的验证器"""
        validators = []
        
        if self.validator_dir.exists():
            for script_file in self.validator_dir.glob('*.py'):
                validators.append(script_file.name)
        
        return sorted(validators)
