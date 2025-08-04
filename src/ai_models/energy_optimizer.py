"""
Simple AI Energy Optimizer
==========================

A simplified rule-based energy optimizer that works without TensorFlow dependencies.
This provides intelligent energy source selection based on environmental conditions.
"""

import numpy as np
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class EnergyOptimizer:
    """Simple rule-based energy source optimization engine."""
    
    def __init__(self, config=None):
        """Initialize the energy optimizer."""
        self.config = config or {}
        self.name = "Simple Energy Optimizer"
        self.version = "1.0"
        
        # Decision thresholds
        self.solar_thresholds = {
            'good_irradiance': 600,
            'moderate_irradiance': 300,
            'min_irradiance': 100
        }
        
        self.thermal_thresholds = {
            'good_temp': 25,
            'excellent_temp': 30,
            'min_wind': 5
        }
        
        self.battery_thresholds = {
            'high_level': 80,
            'good_level': 50,
            'low_level': 20,
            'critical_level': 10
        }
        
        logger.info(f"Initialized {self.name} v{self.version}")
    
    def predict_optimal_source(self, sensor_data):
        """
        Predict optimal energy source based on sensor data.
        Returns: energy source string ('solar', 'thermal', 'battery')
        """
        # Convert sensor data to standardized format
        standardized_data = self._standardize_sensor_data(sensor_data)
        
        # Get prediction from rule-based system
        prediction, confidence, scores = self._predict_energy_source(standardized_data)
        
        # Convert prediction index to source name
        sources = ['solar', 'thermal', 'battery']
        optimal_source = sources[prediction]
        
        logger.info(f"AI Prediction: {optimal_source} (confidence: {confidence:.2%})")
        
        return optimal_source
    
    def _standardize_sensor_data(self, sensor_data):
        """Convert various sensor data formats to standardized format."""
        # Extract values with defaults
        standardized = {
            'solar_irradiance': sensor_data.get('solar_irradiance', 
                                               sensor_data.get('solar_voltage', 0) * 50),
            'temperature': sensor_data.get('temperature', 
                                         sensor_data.get('ambient_temperature', 20)),
            'humidity': sensor_data.get('humidity', 50),
            'battery_level': sensor_data.get('battery_level', 
                                           sensor_data.get('battery_soc', 50)),
            'power_demand': sensor_data.get('power_demand', 
                                          sensor_data.get('load_demand', 100)),
            'wind_speed': sensor_data.get('wind_speed', 0),
            'time_of_day': sensor_data.get('time_of_day', 
                                         sensor_data.get('hour_of_day', 12)),
            'weather_condition': sensor_data.get('weather_condition', 'clear'),
            'season': sensor_data.get('season', 'summer')
        }
        
        return standardized
    
    def _predict_energy_source(self, sensor_data):
        """
        Predict optimal energy source using rule-based logic.
        Returns: (prediction_index, confidence, scores_dict)
        """
        # Extract sensor values
        solar_irradiance = sensor_data.get('solar_irradiance', 0)
        temperature = sensor_data.get('temperature', 20)
        humidity = sensor_data.get('humidity', 50)
        battery_level = sensor_data.get('battery_level', 50)
        power_demand = sensor_data.get('power_demand', 100)
        wind_speed = sensor_data.get('wind_speed', 0)
        time_of_day = sensor_data.get('time_of_day', 12)
        
        # Initialize scores
        solar_score = 0
        thermal_score = 0
        battery_score = 0
        
        # Solar power scoring
        if solar_irradiance > self.solar_thresholds['good_irradiance']:
            solar_score += 3
        elif solar_irradiance > self.solar_thresholds['moderate_irradiance']:
            solar_score += 2
        elif solar_irradiance > self.solar_thresholds['min_irradiance']:
            solar_score += 1
            
        # Time of day bonus for solar (6 AM to 6 PM)
        if 6 <= time_of_day <= 18:
            solar_score += 1
            
        # Thermal power scoring
        if temperature > self.thermal_thresholds['excellent_temp']:
            thermal_score += 3
        elif temperature > self.thermal_thresholds['good_temp']:
            thermal_score += 2
            
        # Wind helps thermal systems
        if wind_speed > self.thermal_thresholds['min_wind']:
            thermal_score += 1
            
        # Battery scoring
        if battery_level > self.battery_thresholds['high_level']:
            battery_score += 2
        elif battery_level > self.battery_thresholds['good_level']:
            battery_score += 1
            
        # Penalty for low battery
        if battery_level < self.battery_thresholds['low_level']:
            battery_score -= 3
        elif battery_level < self.battery_thresholds['critical_level']:
            battery_score -= 5
            
        # High demand favors stable sources
        if power_demand > 150:
            thermal_score += 1
            battery_score += 1
            
        # Night time adjustments
        if time_of_day < 6 or time_of_day > 18:
            thermal_score += 1
            battery_score += 1
            solar_score -= 2
            
        # Weather adjustments
        weather = sensor_data.get('weather_condition', '').lower()
        if 'cloudy' in weather or 'overcast' in weather:
            solar_score -= 1
            thermal_score += 1
        elif 'rain' in weather or 'storm' in weather:
            solar_score -= 2
            battery_score += 1
        elif 'sunny' in weather or 'clear' in weather:
            solar_score += 1
            
        # Find the best option
        scores = [solar_score, thermal_score, battery_score]
        prediction = scores.index(max(scores))
        
        # Calculate confidence
        max_score = max(scores)
        total_positive_score = sum(max(0, score) for score in scores)
        confidence = max_score / (total_positive_score + 0.1) if total_positive_score > 0 else 0.5
        
        return prediction, confidence, {
            'solar_score': solar_score,
            'thermal_score': thermal_score,
            'battery_score': battery_score
        }
    
    def update_model(self, sensor_data, chosen_source):
        """Update model with recent performance data (placeholder for future ML)."""
        # In a full ML implementation, this would update the neural network
        # For now, we just log the decision for future analysis
        logger.debug(f"Decision logged: {chosen_source} chosen for conditions: {sensor_data}")
        pass
    
    def get_model_info(self):
        """Get information about the current model."""
        return {
            'name': self.name,
            'version': self.version,
            'type': 'rule_based',
            'features': list(self.solar_thresholds.keys()) + 
                       list(self.thermal_thresholds.keys()) + 
                       list(self.battery_thresholds.keys())
        }
    
    def explain_decision(self, sensor_data):
        """Provide detailed explanation of energy source decision."""
        standardized_data = self._standardize_sensor_data(sensor_data)
        prediction, confidence, scores = self._predict_energy_source(standardized_data)
        
        sources = ['Solar Power', 'Thermal Energy', 'Battery Power']
        chosen_source = sources[prediction]
        
        explanation = {
            'chosen_source': chosen_source,
            'confidence': confidence,
            'reasoning': self._generate_reasoning(standardized_data, scores, prediction),
            'scores': scores,
            'sensor_analysis': self._analyze_sensors(standardized_data)
        }
        
        return explanation
    
    def _generate_reasoning(self, sensor_data, scores, prediction):
        """Generate human-readable reasoning for the decision."""
        reasons = []
        
        if prediction == 0:  # Solar
            if sensor_data['solar_irradiance'] > 600:
                reasons.append("Excellent solar irradiance detected")
            if 6 <= sensor_data['time_of_day'] <= 18:
                reasons.append("Daytime hours favor solar energy")
            if sensor_data['battery_level'] > 50:
                reasons.append("Battery level adequate for solar operation")
                
        elif prediction == 1:  # Thermal
            if sensor_data['temperature'] > 30:
                reasons.append("High temperature excellent for thermal energy")
            if sensor_data['wind_speed'] > 5:
                reasons.append("Wind conditions support thermal efficiency")
            if sensor_data['power_demand'] > 150:
                reasons.append("High power demand suits thermal stability")
                
        else:  # Battery
            if sensor_data['time_of_day'] < 6 or sensor_data['time_of_day'] > 18:
                reasons.append("Night time favors battery usage")
            if sensor_data['solar_irradiance'] < 100:
                reasons.append("Low solar availability requires battery backup")
            if sensor_data['battery_level'] > 80:
                reasons.append("High battery level available for use")
        
        return reasons if reasons else ["Default decision based on current conditions"]
    
    def _analyze_sensors(self, sensor_data):
        """Analyze individual sensor readings."""
        analysis = {}
        
        # Solar analysis
        irradiance = sensor_data['solar_irradiance']
        if irradiance > 600:
            analysis['solar'] = "Excellent"
        elif irradiance > 300:
            analysis['solar'] = "Good"
        elif irradiance > 100:
            analysis['solar'] = "Fair"
        else:
            analysis['solar'] = "Poor"
            
        # Thermal analysis
        temp = sensor_data['temperature']
        if temp > 30:
            analysis['thermal'] = "Excellent"
        elif temp > 25:
            analysis['thermal'] = "Good"
        else:
            analysis['thermal'] = "Fair"
            
        # Battery analysis
        battery = sensor_data['battery_level']
        if battery > 80:
            analysis['battery'] = "Excellent"
        elif battery > 50:
            analysis['battery'] = "Good"
        elif battery > 20:
            analysis['battery'] = "Fair"
        else:
            analysis['battery'] = "Critical"
            
        return analysis
