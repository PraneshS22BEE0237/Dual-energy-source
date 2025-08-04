#!/usr/bin/env python3
"""
Quick Start Demo for Dual Energy Source Management System
========================================================

This script provides a quick demonstration of the AI model in action.
Run this to see how the system makes intelligent energy decisions.
"""

import sys
import os
import time
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from ai_models.energy_optimizer import EnergyOptimizer
    from hardware.sensor_manager import SensorManager
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

def simulate_day_cycle():
    """Simulate a full day cycle and show AI decisions"""
    
    print("🌞⚡🔋 DUAL ENERGY SOURCE AI DEMO")
    print("=" * 50)
    print("Simulating 24-hour energy optimization cycle")
    print("Watch the AI make intelligent decisions!\n")
    
    # Initialize AI model
    optimizer = EnergyOptimizer()
    
    # Simulate different times of day
    scenarios = [
        (6, "Early Morning", {"solar_irradiance": 200, "temperature": 18, "battery_level": 70, "power_demand": 80}),
        (9, "Morning", {"solar_irradiance": 600, "temperature": 22, "battery_level": 65, "power_demand": 120}),
        (12, "Noon", {"solar_irradiance": 900, "temperature": 28, "battery_level": 85, "power_demand": 140}),
        (15, "Afternoon", {"solar_irradiance": 750, "temperature": 32, "battery_level": 90, "power_demand": 160}),
        (18, "Evening", {"solar_irradiance": 300, "temperature": 25, "battery_level": 80, "power_demand": 180}),
        (21, "Night", {"solar_irradiance": 0, "temperature": 20, "battery_level": 75, "power_demand": 100}),
        (24, "Late Night", {"solar_irradiance": 0, "temperature": 15, "battery_level": 65, "power_demand": 60}),
    ]
    
    print("Time | Period      | Solar | Temp | Battery | Load | AI Decision     | Confidence")
    print("-" * 80)
    
    for hour, period, conditions in scenarios:
        # Add common conditions
        sensor_data = {
            "time_of_day": hour,
            "humidity": 50,
            "wind_speed": 5,
            "weather_condition": "clear" if conditions["solar_irradiance"] > 0 else "clear_night",
            **conditions
        }
        
        # Get AI prediction
        optimal_source = optimizer.predict_optimal_source(sensor_data)
        explanation = optimizer.explain_decision(sensor_data)
        
        # Format source name for display
        source_display = {
            'solar': '🌞 Solar',
            'thermal': '🌡️ Thermal', 
            'battery': '🔋 Battery'
        }[optimal_source]
        
        # Display results
        print(f"{hour:2d}:00| {period:11s} | {conditions['solar_irradiance']:4d}  | {conditions['temperature']:2d}°C | "
              f"{conditions['battery_level']:3d}%    | {conditions['power_demand']:3d}W | {source_display:15s} | "
              f"{explanation['confidence']:.1%}")
        
        # Brief pause for dramatic effect
        time.sleep(0.5)
    
    print("-" * 80)
    print("\n🎯 Key Observations:")
    print("• Morning: Solar power becomes available and preferred")
    print("• Noon: Peak solar conditions, highest efficiency")  
    print("• Hot afternoon: Thermal energy utilized for high temps")
    print("• Evening: Transition to battery as solar decreases")
    print("• Night: Battery backup maintains power supply")
    print("\nThe AI automatically optimizes for maximum efficiency! 🚀")

def test_your_scenario():
    """Allow user to test custom scenario"""
    
    print("\n" + "=" * 50)
    print("🧪 TEST YOUR OWN SCENARIO")
    print("=" * 50)
    
    optimizer = EnergyOptimizer()
    
    # Get user input
    print("Enter your scenario (press Enter for defaults):")
    
    try:
        solar = input("Solar Irradiance (0-1000 W/m²) [500]: ").strip()
        solar_irradiance = int(solar) if solar else 500
        
        temp = input("Temperature (°C) [25]: ").strip()
        temperature = int(temp) if temp else 25
        
        battery = input("Battery Level (%) [70]: ").strip()
        battery_level = int(battery) if battery else 70
        
        demand = input("Power Demand (W) [120]: ").strip()
        power_demand = int(demand) if demand else 120
        
        hour = input("Time of Day (0-23) [14]: ").strip()
        time_of_day = int(hour) if hour else 14
        
    except ValueError:
        print("Using default values...")
        solar_irradiance = 500
        temperature = 25
        battery_level = 70
        power_demand = 120
        time_of_day = 14
    
    # Create sensor data
    sensor_data = {
        'solar_irradiance': solar_irradiance,
        'temperature': temperature,
        'humidity': 50,
        'battery_level': battery_level,
        'power_demand': power_demand,
        'wind_speed': 5,
        'time_of_day': time_of_day,
        'weather_condition': 'clear'
    }
    
    # Get AI decision
    optimal_source = optimizer.predict_optimal_source(sensor_data)
    explanation = optimizer.explain_decision(sensor_data)
    
    # Display results
    print(f"\n📊 YOUR SCENARIO RESULTS:")
    print(f"🌞 Solar: {solar_irradiance} W/m² | 🌡️ Temp: {temperature}°C | 🔋 Battery: {battery_level}% | ⚡ Load: {power_demand}W")
    print(f"🕐 Time: {time_of_day}:00")
    print(f"\n🤖 AI RECOMMENDATION: {explanation['chosen_source']} ({explanation['confidence']:.1%} confidence)")
    print(f"\n💡 Reasoning:")
    for reason in explanation['reasoning']:
        print(f"   • {reason}")
    
    scores = explanation['scores']
    print(f"\n📈 Scoring Breakdown:")
    print(f"   🌞 Solar Power: {scores['solar_score']:+d} points")
    print(f"   🌡️ Thermal Energy: {scores['thermal_score']:+d} points") 
    print(f"   🔋 Battery Power: {scores['battery_score']:+d} points")

def main():
    """Main demo function"""
    
    try:
        # Run day cycle simulation
        simulate_day_cycle()
        
        # Ask if user wants to test custom scenario
        print(f"\n{'='*50}")
        test_custom = input("Would you like to test your own scenario? (y/n): ").strip().lower()
        
        if test_custom in ['y', 'yes']:
            test_your_scenario()
        
        print(f"\n{'='*50}")
        print("🎉 DEMO COMPLETE!")
        print("Ready to deploy your AI-powered energy system!")
        print("Run 'python src/main.py' to start the full system.")
        print("Visit http://localhost:5000 for the web dashboard.")
        print("Check tests/custom_test.py for interactive testing.")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Goodbye! 👋")
    except Exception as e:
        print(f"\nDemo error: {e}")
        print("Check your installation and try again.")

if __name__ == "__main__":
    main()
