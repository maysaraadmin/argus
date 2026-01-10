#!/usr/bin/env python3
"""
Configuration management for Argus MVP
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    url: str = "postgresql://argus:argus@localhost/argus"
    pool_size: int = 10
    max_overflow: int = 20


@dataclass
class RedisConfig:
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None


@dataclass
class APIConfig:
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False
    cors_origins: list = None
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]


@dataclass
class EntityResolutionConfig:
    similarity_threshold: float = 0.85
    possible_match_threshold: float = 0.65
    non_match_threshold: float = 0.3
    
    weights: Dict[str, float] = None
    
    def __post_init__(self):
        if self.weights is None:
            self.weights = {
                "name": 0.4,
                "dob": 0.3,
                "address": 0.2,
                "phone": 0.1
            }


@dataclass
class LoggingConfig:
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None


class Config:
    """Central configuration management"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config_file()
        self._config_data = {}
        self._load_config()
    
    def _find_config_file(self) -> str:
        """Find configuration file in standard locations"""
        possible_paths = [
            "config/dev.yaml",
            "config/config.yaml",
            os.path.expanduser("~/.argus/config.yaml"),
            "/etc/argus/config.yaml"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Return default if no config found
        return "config/dev.yaml"
    
    def _load_config(self):
        """Load configuration from file and environment variables"""
        # Load from file if it exists
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self._config_data = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Warning: Could not load config file {self.config_path}: {e}")
                self._config_data = {}
        
        # Override with environment variables
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        env_mappings = {
            "ARGUS_DATABASE_URL": ["database", "url"],
            "ARGUS_REDIS_HOST": ["redis", "host"],
            "ARGUS_REDIS_PORT": ["redis", "port"],
            "ARGUS_API_HOST": ["api", "host"],
            "ARGUS_API_PORT": ["api", "port"],
            "ARGUS_LOG_LEVEL": ["logging", "level"],
            "ARGUS_DEBUG": ["api", "debug"],
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                self._set_nested_value(config_path, value)
    
    def _set_nested_value(self, path: list, value: Any):
        """Set nested configuration value"""
        current = self._config_data
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Type conversion
        if path[-1] in ["port", "pool_size", "max_overflow"]:
            value = int(value)
        elif path[-1] in ["debug"]:
            value = value.lower() in ("true", "1", "yes")
        
        current[path[-1]] = value
    
    @property
    def database(self) -> DatabaseConfig:
        """Get database configuration"""
        db_config = self._config_data.get("database", {})
        return DatabaseConfig(**db_config)
    
    @property
    def redis(self) -> RedisConfig:
        """Get Redis configuration"""
        redis_config = self._config_data.get("redis", {})
        return RedisConfig(**redis_config)
    
    @property
    def api(self) -> APIConfig:
        """Get API configuration"""
        api_config = self._config_data.get("api", {})
        return APIConfig(**api_config)
    
    @property
    def entity_resolution(self) -> EntityResolutionConfig:
        """Get entity resolution configuration"""
        er_config = self._config_data.get("entity_resolution", {})
        return EntityResolutionConfig(**er_config)
    
    @property
    def logging(self) -> LoggingConfig:
        """Get logging configuration"""
        log_config = self._config_data.get("logging", {})
        return LoggingConfig(**log_config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        keys = key.split(".")
        current = self._config_data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current
    
    def set(self, key: str, value: Any):
        """Set configuration value by key (supports dot notation)"""
        keys = key.split(".")
        current = self._config_data
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def reload(self):
        """Reload configuration from file"""
        self._load_config()


# Global configuration instance
config = Config()