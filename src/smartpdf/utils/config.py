"""Configuration management."""
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for SmartPDF-Science."""
    
    def __init__(self, config_path: Optional[str | Path] = None):
        """Initialize configuration.
        
        Args:
            config_path: Path to YAML config file. If None, uses default.
        """
        if config_path is None:
            # Try to find config in standard locations
            possible_paths = [
                Path("configs/default.yaml"),
                Path(__file__).parent.parent.parent.parent / "configs" / "default.yaml",
            ]
            
            for path in possible_paths:
                if path.exists():
                    config_path = path
                    break
        
        if config_path is None:
            logger.warning("No config file found, using defaults")
            self.config = self._get_default_config()
        else:
            logger.info(f"Loading config from: {config_path}")
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'ocr.device')
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self, path: str | Path) -> None:
        """Save configuration to file.
        
        Args:
            path: Path to save YAML file
        """
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
        logger.info(f"Config saved to: {path}")
    
    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "ocr": {
                "device": "gpu:0",
                "use_layout_detection": True,
                "use_formula_recognition": True,
                "formula_model": "PP-FormulaNet_plus-L",
                "use_doc_orientation_classify": True,
                "use_doc_unwarping": False
            },
            "filter": {
                "min_area": 5000,
                "min_text_len": 15,
                "min_score": 0.65
            },
            "llm": {
                "model_name": "Qwen/Qwen3-8B",
                "device": "cuda",
                "load_in_4bit": False,
                "correction_mode": "auto"
            },
            "output": {
                "default_format": "docx",
                "save_images": True,
                "image_quality": 92
            },
            "logging": {
                "level": "INFO",
                "file": "smartpdf.log",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }


# Global config instance
_config_instance: Optional[Config] = None


def get_config(config_path: Optional[str | Path] = None) -> Config:
    """Get global configuration instance.
    
    Args:
        config_path: Path to config file (only used on first call)
    
    Returns:
        Config instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_path)
    return _config_instance