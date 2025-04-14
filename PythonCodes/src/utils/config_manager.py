import os
import json
import yaml
from typing import Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field
from .error_handling import KAPESITError, ErrorSeverity

@dataclass
class Config:
    """Configuration class for KAPESIT"""
    # Core settings
    debug_mode: bool = False
    log_level: str = "INFO"
    log_file: str = "kapesit.log"
    
    # API settings
    api_host: str = "localhost"
    api_port: int = 8000
    api_timeout: int = 30
    
    # Database settings
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "kapesit"
    db_user: str = "postgres"
    db_password: str = ""
    
    # Cache settings
    cache_enabled: bool = True
    cache_ttl: int = 3600
    cache_max_size: int = 1000
    
    # Security settings
    jwt_secret: str = ""
    jwt_expiry: int = 3600
    cors_origins: list = field(default_factory=list)
    
    # Feature flags
    features: Dict[str, bool] = field(default_factory=dict)
    
    # Custom settings
    custom: Dict[str, Any] = field(default_factory=dict)

class ConfigManager:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.getenv("KAPESIT_CONFIG", "config.yaml")
        self.config = Config()
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file"""
        try:
            config_path = Path(self.config_path)
            if not config_path.exists():
                raise KAPESITError(
                    f"Configuration file not found: {self.config_path}",
                    severity=ErrorSeverity.ERROR,
                    component="CONFIG"
                )
            
            with open(config_path, 'r') as f:
                if config_path.suffix == '.json':
                    config_data = json.load(f)
                elif config_path.suffix in ['.yaml', '.yml']:
                    config_data = yaml.safe_load(f)
                else:
                    raise KAPESITError(
                        f"Unsupported config file format: {config_path.suffix}",
                        severity=ErrorSeverity.ERROR,
                        component="CONFIG"
                    )
            
            self._update_config(config_data)
            
        except Exception as e:
            raise KAPESITError(
                f"Failed to load configuration: {str(e)}",
                severity=ErrorSeverity.CRITICAL,
                component="CONFIG"
            )
    
    def _update_config(self, config_data: Dict[str, Any]) -> None:
        """Update configuration from dictionary"""
        for key, value in config_data.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                self.config.custom[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        if hasattr(self.config, key):
            return getattr(self.config, key)
        return self.config.custom.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
        else:
            self.config.custom[key] = value
    
    def save(self) -> None:
        """Save configuration to file"""
        try:
            config_data = {
                key: getattr(self.config, key)
                for key in self.config.__dataclass_fields__
                if not key.startswith('_')
            }
            config_data.update(self.config.custom)
            
            with open(self.config_path, 'w') as f:
                if Path(self.config_path).suffix == '.json':
                    json.dump(config_data, f, indent=2)
                else:
                    yaml.dump(config_data, f, default_flow_style=False)
                    
        except Exception as e:
            raise KAPESITError(
                f"Failed to save configuration: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="CONFIG"
            )
    
    def reload(self) -> None:
        """Reload configuration from file"""
        self._load_config()
    
    def validate(self) -> bool:
        """Validate configuration"""
        try:
            # Validate required settings
            if not self.config.db_host or not self.config.db_name:
                raise ValueError("Database settings are required")
            
            if not self.config.jwt_secret:
                raise ValueError("JWT secret is required")
            
            # Validate port numbers
            if not (0 < self.config.api_port < 65536):
                raise ValueError("Invalid API port")
            
            if not (0 < self.config.db_port < 65536):
                raise ValueError("Invalid database port")
            
            return True
            
        except Exception as e:
            raise KAPESITError(
                f"Configuration validation failed: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="CONFIG"
            )

# Global configuration instance
config_manager = ConfigManager() 