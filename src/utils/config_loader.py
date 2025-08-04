"""
Configuration Loader
===================

Loads and manages system configuration from YAML files.
"""

import yaml
import os
import logging

logger = logging.getLogger(__name__)

class ConfigLoader:
    """Manages system configuration loading and access."""
    
    def __init__(self, config_path='config/system_config.yaml'):
        """Initialize configuration loader."""
        self.config_path = config_path
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from YAML file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as file:
                    self.config = yaml.safe_load(file) or {}
                logger.info(f"Configuration loaded from {self.config_path}")
            else:
                logger.warning(f"Config file not found: {self.config_path}, using defaults")
                self.config = self.get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.config = self.get_default_config()
    
    def get_default_config(self):
        """Return default configuration."""
        return {
            'control_loop_interval': 5,
            'sensor_read_interval': 1,
            'simulation_mode': True,
            'safety': {
                'solar': {'min_voltage': 12.0, 'min_current': 0.5},
                'thermal': {'min_voltage': 5.0, 'min_temperature': 40.0},
                'battery': {'min_voltage': 10.5, 'critical_voltage': 9.5}
            },
            'gpio': {
                'solar_relay': 18,
                'thermal_relay': 19,
                'battery_relay': 20,
                'emergency_shutdown': 21
            },
            'web': {'host': '0.0.0.0', 'port': 5000, 'debug': False}
        }
    
    def get(self, key, default=None):
        """Get configuration value with optional default."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key, value):
        """Set configuration value."""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as file:
                yaml.dump(self.config, file, default_flow_style=False)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def reload(self):
        """Reload configuration from file."""
        self.load_config()
