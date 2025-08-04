"""
Sensor Manager
==============

Manages all sensor readings for the dual energy system including:
- Solar panel sensors (voltage, current)
- Thermal sensors (temperature, voltage)
- Battery sensors (voltage, current, temperature, SOC)
- Environmental sensors (ambient temperature, humidity)
"""

import time
import threading
import logging
import random
import math
from datetime import datetime
import json

# Hardware-specific imports (commented for development, uncomment for deployment)
try:
    import RPi.GPIO as GPIO
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    from w1thermsensor import W1ThermSensor
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False
    print("Hardware libraries not available - using simulation mode")

logger = logging.getLogger(__name__)

class SensorManager:
    """Manages all sensor readings for the energy system."""
    
    def __init__(self, config):
        """Initialize sensor manager."""
        self.config = config
        self.hardware_available = HARDWARE_AVAILABLE and not config.get('simulation_mode', True)
        self.monitoring = False
        self.sensor_thread = None
        self.latest_readings = {}
        
        # Initialize hardware if available
        if self.hardware_available:
            self.init_hardware()
        else:
            logger.warning("Running in simulation mode - no actual hardware")
            self.init_simulation()
    
    def init_hardware(self):
        """Initialize hardware sensors."""
        logger.info("Initializing hardware sensors")
        
        try:
            # Initialize GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Initialize I2C and ADC
            i2c = busio.I2C(board.SCL, board.SDA)
            self.ads = ADS.ADS1115(i2c)
            
            # Define analog input channels for voltage measurements
            self.solar_voltage_chan = AnalogIn(self.ads, ADS.P0)
            self.thermal_voltage_chan = AnalogIn(self.ads, ADS.P1)
            self.battery_voltage_chan = AnalogIn(self.ads, ADS.P2)
            
            # Initialize temperature sensors
            self.temp_sensors = W1ThermSensor.get_available_sensors()
            
            logger.info("Hardware sensors initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize hardware: {e}")
            logger.warning("Falling back to simulation mode")
            self.hardware_available = False
            self.init_simulation()
    
    def init_simulation(self):
        """Initialize simulation mode."""
        logger.info("Initializing sensor simulation")
        
        # Simulation parameters
        self.sim_time_start = time.time()
        self.sim_params = {
            'solar_base': 500,
            'thermal_base': 40,
            'battery_base': 75,
            'noise_level': 0.1
        }
        
    def start_monitoring(self):
        """Start continuous sensor monitoring."""
        if self.monitoring:
            logger.warning("Sensor monitoring already running")
            return
            
        logger.info("Starting sensor monitoring")
        self.monitoring = True
        
        # Start monitoring thread
        self.sensor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.sensor_thread.start()
    
    def stop_monitoring(self):
        """Stop sensor monitoring."""
        logger.info("Stopping sensor monitoring")
        self.monitoring = False
        
        if self.sensor_thread:
            self.sensor_thread.join(timeout=2)
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                # Read all sensors
                readings = self.read_all_sensors()
                
                # Update latest readings
                self.latest_readings = readings
                
                # Log readings periodically
                if time.time() % 60 < 1:  # Every minute
                    logger.debug(f"Sensor readings: {readings}")
                
                # Wait before next reading
                time.sleep(self.config.get('sensor_read_interval', 1))
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1)
    
    def read_all_sensors(self):
        """Read all sensor values."""
        if self.hardware_available:
            return self._read_hardware_sensors()
        else:
            return self._read_simulated_sensors()
    
    def _read_hardware_sensors(self):
        """Read actual hardware sensors."""
        readings = {}
        
        try:
            # Solar panel readings
            solar_voltage_raw = self.solar_voltage_chan.voltage
            readings['solar_voltage'] = solar_voltage_raw * 5.0  # Scale for voltage divider
            readings['solar_current'] = self._read_current_sensor('solar')
            readings['solar_power'] = readings['solar_voltage'] * readings['solar_current']
            
            # Thermal readings
            thermal_voltage_raw = self.thermal_voltage_chan.voltage
            readings['thermal_voltage'] = thermal_voltage_raw * 3.0
            readings['thermal_current'] = self._read_current_sensor('thermal')
            readings['thermal_temperature'] = self._read_thermal_temperature()
            
            # Battery readings
            battery_voltage_raw = self.battery_voltage_chan.voltage
            readings['battery_voltage'] = battery_voltage_raw * 4.0
            readings['battery_current'] = self._read_current_sensor('battery')
            readings['battery_temperature'] = self._read_battery_temperature()
            readings['battery_soc'] = self._calculate_battery_soc(readings['battery_voltage'])
            
            # Environmental readings
            readings['ambient_temperature'] = self._read_ambient_temperature()
            readings['humidity'] = self._read_humidity()
            
            # Calculated values
            readings['hour_of_day'] = datetime.now().hour
            readings['day_of_year'] = datetime.now().timetuple().tm_yday
            readings['load_demand'] = self._calculate_load_demand()
            
            # Add timestamp
            readings['timestamp'] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Error reading hardware sensors: {e}")
            # Fall back to simulation if hardware fails
            readings = self._read_simulated_sensors()
        
        return readings
    
    def _read_simulated_sensors(self):
        """Generate realistic simulated sensor readings."""
        current_time = time.time()
        elapsed = current_time - self.sim_time_start
        hour = datetime.now().hour
        day = datetime.now().timetuple().tm_yday
        
        # Solar simulation (varies with time of day and some randomness)
        solar_factor = max(0, math.sin((hour - 6) * math.pi / 12)) if 6 <= hour <= 18 else 0
        solar_irradiance = (500 + 300 * solar_factor + 
                           random.uniform(-50, 50) + 
                           100 * math.sin(elapsed / 3600))  # Slow variation
        
        solar_voltage = 12.0 + 2.0 * solar_factor + random.uniform(-0.5, 0.5)
        solar_current = max(0, 2.0 * solar_factor + random.uniform(-0.3, 0.3))
        
        # Thermal simulation (more stable, temperature dependent)
        thermal_temp = 40 + 20 * math.sin(elapsed / 7200) + random.uniform(-5, 5)
        thermal_voltage = max(0, (thermal_temp - 30) * 0.3 + random.uniform(-1, 1))
        thermal_current = thermal_voltage * 0.8 if thermal_voltage > 3 else 0
        
        # Battery simulation (slowly decreases unless charging)
        battery_base = 75 - (elapsed / 36000) % 60  # Slow discharge cycle
        battery_soc = max(20, min(100, battery_base + random.uniform(-5, 5)))
        battery_voltage = 10.5 + (battery_soc / 100) * 3.0 + random.uniform(-0.2, 0.2)
        battery_current = 1.5 + random.uniform(-0.5, 0.5)
        battery_temp = 25 + random.uniform(-3, 8)
        
        # Environmental simulation
        ambient_temp = 20 + 10 * math.sin((hour - 12) * math.pi / 12) + random.uniform(-2, 2)
        humidity = 50 + 20 * math.sin(elapsed / 5400) + random.uniform(-10, 10)
        
        # Load demand simulation (higher during day)
        load_base = 80 + 40 * (0.5 + 0.5 * math.sin((hour - 6) * math.pi / 12))
        load_demand = max(50, load_base + random.uniform(-20, 20))
        
        readings = {
            # Solar readings
            'solar_voltage': round(solar_voltage, 2),
            'solar_current': round(solar_current, 2),
            'solar_power': round(solar_voltage * solar_current, 2),
            'solar_irradiance': round(solar_irradiance, 1),
            
            # Thermal readings
            'thermal_voltage': round(thermal_voltage, 2),
            'thermal_current': round(thermal_current, 2),
            'thermal_temperature': round(thermal_temp, 1),
            
            # Battery readings
            'battery_voltage': round(battery_voltage, 2),
            'battery_current': round(battery_current, 2),
            'battery_soc': round(battery_soc, 1),
            'battery_level': round(battery_soc, 1),  # Alias for compatibility
            'battery_temperature': round(battery_temp, 1),
            
            # Environmental readings
            'ambient_temperature': round(ambient_temp, 1),
            'temperature': round(ambient_temp, 1),  # Alias for compatibility
            'humidity': round(max(30, min(90, humidity)), 1),
            
            # System readings
            'hour_of_day': hour,
            'time_of_day': hour,  # Alias for compatibility
            'day_of_year': day,
            'load_demand': round(load_demand, 1),
            'power_demand': round(load_demand, 1),  # Alias for compatibility
            'wind_speed': round(random.uniform(0, 15), 1),
            
            # Metadata
            'timestamp': datetime.now().isoformat(),
            'simulation_mode': True
        }
        
        return readings
    
    def _read_current_sensor(self, sensor_type):
        """Read current sensor for specified type."""
        # Placeholder for actual current sensor reading
        # This would use ACS712 or similar current sensors
        return random.uniform(0.5, 3.0)
    
    def _read_thermal_temperature(self):
        """Read thermal sensor temperature."""
        # Placeholder for thermistor or thermocouple reading
        return random.uniform(40, 80)
    
    def _read_battery_temperature(self):
        """Read battery temperature sensor."""
        # Placeholder for battery temperature sensor
        return random.uniform(20, 35)
    
    def _read_ambient_temperature(self):
        """Read ambient temperature sensor."""
        # Placeholder for DHT22 or similar sensor
        return random.uniform(15, 35)
    
    def _read_humidity(self):
        """Read humidity sensor."""
        # Placeholder for DHT22 humidity reading
        return random.uniform(40, 80)
    
    def _calculate_battery_soc(self, voltage):
        """Calculate battery State of Charge from voltage."""
        # Simple linear approximation (should be calibrated for specific battery)
        min_voltage = 10.5
        max_voltage = 13.5
        soc = ((voltage - min_voltage) / (max_voltage - min_voltage)) * 100
        return max(0, min(100, soc))
    
    def _calculate_load_demand(self):
        """Calculate current load demand."""
        # Placeholder - would measure actual load current
        hour = datetime.now().hour
        base_load = 80 + 40 * (0.5 + 0.5 * math.sin((hour - 6) * math.pi / 12))
        return base_load + random.uniform(-10, 10)
    
    def get_all_readings(self):
        """Get the latest sensor readings."""
        if not self.latest_readings:
            # If no readings yet, get them immediately
            self.latest_readings = self.read_all_sensors()
        
        return self.latest_readings.copy()
    
    def get_sensor_status(self):
        """Get status of all sensors."""
        readings = self.get_all_readings()
        
        status = {
            'hardware_available': self.hardware_available,
            'monitoring': self.monitoring,
            'last_reading': readings.get('timestamp'),
            'sensor_health': {
                'solar': 'ok' if readings.get('solar_voltage', 0) > 0 else 'error',
                'thermal': 'ok' if readings.get('thermal_voltage', 0) >= 0 else 'error',
                'battery': 'ok' if readings.get('battery_voltage', 0) > 10 else 'low',
                'environmental': 'ok'
            }
        }
        
        return status
    
    def calibrate_sensors(self):
        """Calibrate sensors (placeholder for future implementation)."""
        logger.info("Sensor calibration not yet implemented")
        pass
    
    def cleanup(self):
        """Clean up resources."""
        self.stop_monitoring()
        
        if self.hardware_available:
            try:
                GPIO.cleanup()
            except:
                pass
