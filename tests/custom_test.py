"""
Custom Sensor Input Testing for Dual Energy Source AI Model
This script allows you to input your own sensor readings to test the AI model
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from ai_models.energy_optimizer import EnergyOptimizer

def get_user_input():
    """Get sensor readings from user input"""
    print("\n" + "="*50)
    print("ENTER YOUR CUSTOM SENSOR READINGS")
    print("="*50)
    print("Please enter the following sensor values:")
    print("(Press Enter for default values shown in brackets)")
    print()
    
    try:
        # Solar Irradiance
        solar_input = input("Solar Irradiance (0-1000 W/m²) [500]: ").strip()
        solar_irradiance = int(solar_input) if solar_input else 500
        
        # Temperature
        temp_input = input("Temperature (10-40°C) [25]: ").strip()
        temperature = int(temp_input) if temp_input else 25
        
        # Humidity
        humidity_input = input("Humidity (30-90%) [60]: ").strip()
        humidity = int(humidity_input) if humidity_input else 60
        
        # Battery Level
        battery_input = input("Battery Level (0-100%) [70]: ").strip()
        battery_level = int(battery_input) if battery_input else 70
        
        # Power Demand
        demand_input = input("Power Demand (50-300 W) [120]: ").strip()
        power_demand = int(demand_input) if demand_input else 120
        
        # Wind Speed
        wind_input = input("Wind Speed (0-20 m/s) [5]: ").strip()
        wind_speed = int(wind_input) if wind_input else 5
        
        # Time of Day
        time_input = input("Time of Day (0-23 hours) [14]: ").strip()
        time_of_day = int(time_input) if time_input else 14
        
        # Weather condition (optional)
        weather_input = input("Weather Condition [sunny]: ").strip()
        weather_condition = weather_input if weather_input else "sunny"
        
        # Validate ranges
        solar_irradiance = max(0, min(1000, solar_irradiance))
        temperature = max(10, min(40, temperature))
        humidity = max(30, min(90, humidity))
        battery_level = max(0, min(100, battery_level))
        power_demand = max(50, min(300, power_demand))
        wind_speed = max(0, min(20, wind_speed))
        time_of_day = max(0, min(23, time_of_day))
        
        return {
            'solar_irradiance': solar_irradiance,
            'temperature': temperature,
            'humidity': humidity,
            'battery_level': battery_level,
            'power_demand': power_demand,
            'wind_speed': wind_speed,
            'time_of_day': time_of_day,
            'weather_condition': weather_condition
        }
        
    except ValueError:
        print("Invalid input! Using default values.")
        return {
            'solar_irradiance': 500,
            'temperature': 25,
            'humidity': 60,
            'battery_level': 70,
            'power_demand': 120,
            'wind_speed': 5,
            'time_of_day': 14,
            'weather_condition': 'sunny'
        }

def test_custom_scenario():
    """Test the AI model with custom user input"""
    
    print("="*60)
    print("DUAL ENERGY SOURCE AI MODEL - CUSTOM INPUT TEST")
    print("="*60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize the AI model
    optimizer = EnergyOptimizer()
    
    energy_sources = ['Solar Power', 'Thermal Energy', 'Battery Power']
    
    while True:
        # Get custom sensor data from user
        sensor_data = get_user_input()
        
        print("\n" + "-"*50)
        print("YOUR INPUT SUMMARY:")
        print("-"*50)
        print(f"Solar Irradiance: {sensor_data['solar_irradiance']} W/m²")
        print(f"Temperature: {sensor_data['temperature']}°C")
        print(f"Humidity: {sensor_data['humidity']}%")
        print(f"Battery Level: {sensor_data['battery_level']}%")
        print(f"Power Demand: {sensor_data['power_demand']} W")
        print(f"Wind Speed: {sensor_data['wind_speed']} m/s")
        print(f"Time of Day: {sensor_data['time_of_day']}:00")
        print(f"Weather: {sensor_data['weather_condition']}")
        
        # Get AI prediction
        optimal_source = optimizer.predict_optimal_source(sensor_data)
        explanation = optimizer.explain_decision(sensor_data)
        
        print("\n" + "="*50)
        print("AI MODEL ANALYSIS RESULTS:")
        print("="*50)
        print(f"RECOMMENDED ENERGY SOURCE: {explanation['chosen_source']}")
        print(f"Confidence Level: {explanation['confidence']:.2%}")
        print()
        print("Detailed Scoring:")
        scores = explanation['scores']
        print(f"  Solar Power Score:  {scores['solar_score']:+2d}")
        print(f"  Thermal Energy Score: {scores['thermal_score']:+2d}")
        print(f"  Battery Power Score:  {scores['battery_score']:+2d}")
        print()
        
        print(f"AI Reasoning:")
        for reason in explanation['reasoning']:
            print(f"  • {reason}")
        
        print(f"\nSensor Analysis:")
        analysis = explanation['sensor_analysis']
        print(f"  • Solar Conditions: {analysis['solar']}")
        print(f"  • Thermal Conditions: {analysis['thermal']}")
        print(f"  • Battery Status: {analysis['battery']}")
        
        print("\n" + "="*60)
        
        # Ask if user wants to test another scenario
        while True:
            continue_test = input("\nWould you like to test another scenario? (y/n): ").strip().lower()
            if continue_test in ['y', 'yes']:
                break
            elif continue_test in ['n', 'no']:
                print("\nThank you for testing the Dual Energy Source AI Model!")
                print("The system is ready for real hardware integration!")
                return
            else:
                print("Please enter 'y' for yes or 'n' for no.")

if __name__ == "__main__":
    try:
        test_custom_scenario()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\nError during testing: {e}")
        sys.exit(1)
