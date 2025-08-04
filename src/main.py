#!/usr/bin/env python3
"""
Dual Energy Source Management System - Main Controller
====================================================

This is the main entry point for the dual energy source management system.
It coordinates between solar power, thermal energy, and battery backup using
AI-driven optimization.

Author: AI Assistant
Date: August 2025
"""

import sys
import time
import logging
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

from ai_models.energy_optimizer import EnergyOptimizer
from hardware.sensor_manager import SensorManager
from hardware.power_controller import PowerController
from web.dashboard import create_app
from utils.config_loader import ConfigLoader
from utils.data_logger import DataLogger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class DualEnergySystem:
    """Main system controller for dual energy source management."""
    
    def __init__(self):
        """Initialize the dual energy system."""
        logger.info("Initializing Dual Energy Source Management System")
        
        # Load configuration
        self.config = ConfigLoader('config/system_config.yaml')
        
        # Initialize components
        self.sensor_manager = SensorManager(self.config)
        self.power_controller = PowerController(self.config)
        self.energy_optimizer = EnergyOptimizer(self.config)
        self.data_logger = DataLogger(self.config)
        
        # System state
        self.running = False
        self.current_source = "battery"  # Default to battery
        
    def start_system(self):
        """Start the energy management system."""
        logger.info("Starting energy management system")
        self.running = True
        
        try:
            # Start sensor monitoring
            self.sensor_manager.start_monitoring()
            
            # Start web dashboard in separate thread
            app = create_app(self)
            from threading import Thread
            web_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False))
            web_thread.daemon = True
            web_thread.start()
            
            logger.info("System started successfully")
            logger.info("Web dashboard available at http://localhost:5000")
            
            # Main control loop
            self.control_loop()
            
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")
            self.shutdown()
        except Exception as e:
            logger.error(f"System error: {e}")
            self.shutdown()
    
    def control_loop(self):
        """Main control loop for energy optimization."""
        logger.info("Starting main control loop")
        
        while self.running:
            try:
                # Get current sensor readings
                sensor_data = self.sensor_manager.get_all_readings()
                
                # Use AI model to determine optimal energy source
                optimal_source = self.energy_optimizer.predict_optimal_source(sensor_data)
                
                # Switch energy source if needed
                if optimal_source != self.current_source:
                    self.switch_energy_source(optimal_source, sensor_data)
                
                # Log data
                self.data_logger.log_system_state({
                    'timestamp': datetime.now(),
                    'current_source': self.current_source,
                    'sensor_data': sensor_data,
                    'optimal_source': optimal_source
                })
                
                # Update AI model with recent performance data
                self.energy_optimizer.update_model(sensor_data, self.current_source)
                
                # Monitor system health
                self.check_system_health(sensor_data)
                
                # Wait before next iteration
                time.sleep(self.config.get('control_loop_interval', 5))
                
            except Exception as e:
                logger.error(f"Error in control loop: {e}")
                time.sleep(1)
    
    def switch_energy_source(self, new_source, sensor_data):
        """Switch to a new energy source."""
        logger.info(f"Switching from {self.current_source} to {new_source}")
        
        # Safety checks before switching
        if self.is_safe_to_switch(new_source, sensor_data):
            success = self.power_controller.switch_source(self.current_source, new_source)
            
            if success:
                self.current_source = new_source
                logger.info(f"Successfully switched to {new_source}")
            else:
                logger.warning(f"Failed to switch to {new_source}, staying on {self.current_source}")
        else:
            logger.warning(f"Safety check failed, cannot switch to {new_source}")
    
    def is_safe_to_switch(self, new_source, sensor_data):
        """Check if it's safe to switch to a new energy source."""
        safety_checks = {
            'solar': self.check_solar_safety,
            'thermal': self.check_thermal_safety,
            'battery': self.check_battery_safety
        }
        
        return safety_checks.get(new_source, lambda x: False)(sensor_data)
    
    def check_solar_safety(self, sensor_data):
        """Check if solar power is safe to use."""
        solar_voltage = sensor_data.get('solar_voltage', 0)
        solar_current = sensor_data.get('solar_current', 0)
        
        min_voltage = self.config.get('solar_min_voltage', 12.0)
        min_current = self.config.get('solar_min_current', 0.5)
        
        return solar_voltage >= min_voltage and solar_current >= min_current
    
    def check_thermal_safety(self, sensor_data):
        """Check if thermal energy is safe to use."""
        thermal_voltage = sensor_data.get('thermal_voltage', 0)
        thermal_temp = sensor_data.get('thermal_temperature', 0)
        
        min_voltage = self.config.get('thermal_min_voltage', 5.0)
        max_temp = self.config.get('thermal_max_temperature', 85.0)
        min_temp = self.config.get('thermal_min_temperature', 40.0)
        
        return (thermal_voltage >= min_voltage and 
                min_temp <= thermal_temp <= max_temp)
    
    def check_battery_safety(self, sensor_data):
        """Check if battery is safe to use."""
        battery_voltage = sensor_data.get('battery_voltage', 0)
        battery_temp = sensor_data.get('battery_temperature', 0)
        
        min_voltage = self.config.get('battery_min_voltage', 10.5)
        max_temp = self.config.get('battery_max_temperature', 45.0)
        
        return (battery_voltage >= min_voltage and battery_temp <= max_temp)
    
    def check_system_health(self, sensor_data):
        """Monitor system health and handle emergencies."""
        # Check for emergency conditions
        emergency_conditions = [
            ('battery_voltage', 'low', self.config.get('battery_critical_voltage', 10.0)),
            ('battery_temperature', 'high', self.config.get('battery_critical_temp', 50.0)),
            ('thermal_temperature', 'high', self.config.get('thermal_critical_temp', 90.0))
        ]
        
        for param, condition, threshold in emergency_conditions:
            value = sensor_data.get(param, 0)
            
            if condition == 'low' and value <= threshold:
                self.handle_emergency(f"Critical low {param}: {value}")
            elif condition == 'high' and value >= threshold:
                self.handle_emergency(f"Critical high {param}: {value}")
    
    def handle_emergency(self, message):
        """Handle emergency conditions."""
        logger.critical(f"EMERGENCY: {message}")
        
        # Switch to safest available source (usually battery)
        safe_source = self.find_safest_source()
        if safe_source and safe_source != self.current_source:
            self.power_controller.emergency_switch(safe_source)
            self.current_source = safe_source
        
        # Log emergency
        self.data_logger.log_emergency(message)
    
    def find_safest_source(self):
        """Find the safest available energy source."""
        sensor_data = self.sensor_manager.get_all_readings()
        
        # Priority order: battery > solar > thermal
        if self.check_battery_safety(sensor_data):
            return 'battery'
        elif self.check_solar_safety(sensor_data):
            return 'solar'
        elif self.check_thermal_safety(sensor_data):
            return 'thermal'
        
        return None
    
    def get_system_status(self):
        """Get current system status for web interface."""
        sensor_data = self.sensor_manager.get_all_readings()
        
        return {
            'current_source': self.current_source,
            'sensor_data': sensor_data,
            'system_health': self.get_health_status(sensor_data),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_health_status(self, sensor_data):
        """Get overall system health status."""
        health_checks = [
            self.check_solar_safety(sensor_data),
            self.check_thermal_safety(sensor_data),
            self.check_battery_safety(sensor_data)
        ]
        
        if all(health_checks):
            return 'excellent'
        elif any(health_checks):
            return 'good'
        else:
            return 'critical'
    
    def shutdown(self):
        """Gracefully shutdown the system."""
        logger.info("Shutting down system")
        self.running = False
        
        # Stop monitoring
        self.sensor_manager.stop_monitoring()
        
        # Switch to battery for safety
        self.power_controller.switch_source(self.current_source, 'battery')
        
        # Close data logger
        self.data_logger.close()
        
        logger.info("System shutdown complete")

def main():
    """Main entry point."""
    print("=" * 60)
    print("Dual Energy Source Management System")
    print("AI-Powered Energy Optimization")
    print("=" * 60)
    
    try:
        # Create logs directory
        Path('logs').mkdir(exist_ok=True)
        
        # Initialize and start system
        system = DualEnergySystem()
        system.start_system()
        
    except Exception as e:
        logger.error(f"Failed to start system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
