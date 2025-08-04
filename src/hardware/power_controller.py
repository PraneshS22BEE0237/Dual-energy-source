"""
Power Controller
===============

Controls power relays for switching between energy sources.
Manages solar, thermal, and battery power switching with safety protocols.
"""

import time
import logging

# Hardware-specific imports (commented for development)
try:
    import RPi.GPIO as GPIO
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False
    print("Hardware libraries not available - using simulation mode")

logger = logging.getLogger(__name__)

class PowerController:
    """Manages power switching between energy sources."""
    
    def __init__(self, config):
        """Initialize power controller."""
        self.config = config
        self.hardware_available = HARDWARE_AVAILABLE and not config.get('simulation_mode', True)
        
        # GPIO pin assignments
        self.gpio_pins = {
            'solar': config.get('gpio.solar_relay', 18),
            'thermal': config.get('gpio.thermal_relay', 19),
            'battery': config.get('gpio.battery_relay', 20),
            'emergency': config.get('gpio.emergency_shutdown', 21)
        }
        
        # Current relay states
        self.relay_states = {
            'solar': False,
            'thermal': False,
            'battery': True  # Default to battery for safety
        }
        
        # Initialize hardware if available
        if self.hardware_available:
            self.init_hardware()
        else:
            logger.warning("Running in simulation mode - no actual relay control")
    
    def init_hardware(self):
        """Initialize GPIO pins for relay control."""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Setup relay control pins
            for source, pin in self.gpio_pins.items():
                if source != 'emergency':
                    GPIO.setup(pin, GPIO.OUT)
                    GPIO.output(pin, GPIO.LOW)  # Start with relays off
                else:
                    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Emergency button
            
            # Set default state (battery only)
            self.activate_source('battery')
            
            logger.info("Power controller hardware initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize power controller hardware: {e}")
            self.hardware_available = False
    
    def switch_source(self, from_source, to_source):
        """
        Switch from one energy source to another.
        Returns True if switch was successful.
        """
        logger.info(f"Switching power from {from_source} to {to_source}")
        
        try:
            # Safety check - don't switch if same source
            if from_source == to_source:
                logger.debug("Source already active, no switch needed")
                return True
            
            # Perform the switch with break-before-make logic
            success = self._perform_switch(from_source, to_source)
            
            if success:
                logger.info(f"Successfully switched to {to_source}")
                return True
            else:
                logger.error(f"Failed to switch to {to_source}")
                return False
                
        except Exception as e:
            logger.error(f"Error during power switch: {e}")
            # Emergency fallback to battery
            self.emergency_switch('battery')
            return False
    
    def _perform_switch(self, from_source, to_source):
        """Perform the actual relay switching with safety delays."""
        
        # Step 1: Deactivate current source (break)
        if from_source in self.relay_states:
            self.deactivate_source(from_source)
            
        # Step 2: Safety delay to prevent arcing
        time.sleep(0.1)
        
        # Step 3: Activate new source (make)
        success = self.activate_source(to_source)
        
        return success
    
    def activate_source(self, source):
        """Activate a specific energy source."""
        if source not in self.gpio_pins or source == 'emergency':
            logger.error(f"Invalid energy source: {source}")
            return False
        
        try:
            if self.hardware_available:
                GPIO.output(self.gpio_pins[source], GPIO.HIGH)
            
            self.relay_states[source] = True
            logger.debug(f"Activated {source} relay")
            return True
            
        except Exception as e:
            logger.error(f"Error activating {source}: {e}")
            return False
    
    def deactivate_source(self, source):
        """Deactivate a specific energy source."""
        if source not in self.gpio_pins or source == 'emergency':
            logger.error(f"Invalid energy source: {source}")
            return False
        
        try:
            if self.hardware_available:
                GPIO.output(self.gpio_pins[source], GPIO.LOW)
            
            self.relay_states[source] = False
            logger.debug(f"Deactivated {source} relay")
            return True
            
        except Exception as e:
            logger.error(f"Error deactivating {source}: {e}")
            return False
    
    def emergency_switch(self, safe_source='battery'):
        """Emergency switch to safe source (usually battery)."""
        logger.critical(f"EMERGENCY SWITCH to {safe_source}")
        
        try:
            # Immediately deactivate all sources
            for source in ['solar', 'thermal', 'battery']:
                if self.hardware_available:
                    GPIO.output(self.gpio_pins[source], GPIO.LOW)
                self.relay_states[source] = False
            
            # Brief safety delay
            time.sleep(0.05)
            
            # Activate safe source
            if safe_source:
                self.activate_source(safe_source)
                
            logger.critical(f"Emergency switch to {safe_source} completed")
            
        except Exception as e:
            logger.critical(f"CRITICAL ERROR in emergency switch: {e}")
    
    def get_relay_states(self):
        """Get current relay states."""
        return self.relay_states.copy()
    
    def check_emergency_button(self):
        """Check if emergency stop button is pressed."""
        if not self.hardware_available:
            return False
        
        try:
            # Emergency button is active low (pressed = False)
            button_state = GPIO.input(self.gpio_pins['emergency'])
            return not button_state  # Return True if button is pressed
            
        except Exception as e:
            logger.error(f"Error checking emergency button: {e}")
            return False
    
    def test_relays(self):
        """Test all relays for proper operation."""
        logger.info("Testing all relays")
        
        test_results = {}
        
        for source in ['solar', 'thermal', 'battery']:
            try:
                # Test activation
                logger.debug(f"Testing {source} relay activation")
                activate_success = self.activate_source(source)
                time.sleep(0.5)
                
                # Test deactivation
                logger.debug(f"Testing {source} relay deactivation")
                deactivate_success = self.deactivate_source(source)
                time.sleep(0.5)
                
                test_results[source] = activate_success and deactivate_success
                
            except Exception as e:
                logger.error(f"Error testing {source} relay: {e}")
                test_results[source] = False
        
        # Return to safe state
        self.activate_source('battery')
        
        logger.info(f"Relay test results: {test_results}")
        return test_results
    
    def get_power_status(self):
        """Get comprehensive power system status."""
        status = {
            'hardware_available': self.hardware_available,
            'relay_states': self.get_relay_states(),
            'active_source': self._get_active_source(),
            'emergency_button_pressed': self.check_emergency_button(),
            'last_switch_time': getattr(self, 'last_switch_time', None)
        }
        
        return status
    
    def _get_active_source(self):
        """Determine which source is currently active."""
        active_sources = [source for source, state in self.relay_states.items() if state]
        
        if len(active_sources) == 1:
            return active_sources[0]
        elif len(active_sources) == 0:
            return None
        else:
            logger.warning(f"Multiple sources active: {active_sources}")
            return 'multiple'
    
    def force_source(self, source):
        """Force activation of specific source (override AI decision)."""
        logger.warning(f"Forcing activation of {source} source")
        
        # Deactivate all sources first
        for src in ['solar', 'thermal', 'battery']:
            self.deactivate_source(src)
        
        time.sleep(0.1)
        
        # Activate requested source
        success = self.activate_source(source)
        
        if success:
            logger.warning(f"Forced activation of {source} successful")
        else:
            logger.error(f"Failed to force {source}, reverting to battery")
            self.activate_source('battery')
        
        return success
    
    def cleanup(self):
        """Clean up GPIO resources."""
        logger.info("Cleaning up power controller")
        
        try:
            # Switch to battery for safety
            self.emergency_switch('battery')
            
            # Clean up GPIO
            if self.hardware_available:
                GPIO.cleanup()
                
        except Exception as e:
            logger.error(f"Error during power controller cleanup: {e}")
        
        logger.info("Power controller cleanup complete")
