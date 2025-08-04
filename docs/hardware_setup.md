# Hardware Setup Guide

## Overview

This guide explains how to set up the hardware components for the Dual Energy Source Management System.

## Required Components

### Main Controller
- **Raspberry Pi 4 Model B** (4GB+ recommended)
- **MicroSD Card** (32GB+ Class 10)
- **Power Supply** (5V 3A USB-C)

### Power Management
- **4-Channel Relay Module** (for energy source switching)
- **Solar Panel** (12V, 50W minimum)
- **Thermal Generator** (Peltier or thermoelectric)
- **Battery Pack** (12V Lead-acid or LiFePO4)

### Sensors
- **ADS1115 ADC Module** (16-bit analog-to-digital converter)
- **DS18B20 Temperature Sensors** (waterproof versions)
- **DHT22** (Temperature and humidity sensor)
- **ACS712 Current Sensors** (5A or 20A versions)
- **Voltage Dividers** (for voltage measurement)

### Optional
- **Arduino Uno** (for additional sensor interface)
- **LCD Display** (16x2 or OLED for local display)
- **Breadboard and Jumper Wires**

## Wiring Diagram

### Raspberry Pi Connections

```
GPIO Pin    | Connection
------------|------------------
GPIO 18     | Solar Relay IN1
GPIO 19     | Thermal Relay IN2  
GPIO 20     | Battery Relay IN3
GPIO 21     | Emergency Stop
GPIO 2 (SDA)| I2C Data
GPIO 3 (SCL)| I2C Clock
5V          | Relay Module VCC
GND         | Common Ground
```

### Relay Module Connections

```
Relay       | Normally Open | Common    | Load
------------|---------------|-----------|-------------
Solar       | Solar +       | Load +    | To Load
Thermal     | Thermal +     | Load +    | To Load  
Battery     | Battery +     | Load +    | To Load
```

### Sensor Connections

```
ADS1115 ADC:
- VCC → 3.3V
- GND → Ground
- SDA → GPIO 2
- SCL → GPIO 3
- A0 → Solar Voltage Divider
- A1 → Thermal Voltage Divider
- A2 → Battery Voltage Divider
- A3 → Additional Sensor

DS18B20 Temperature:
- VCC → 3.3V
- Data → GPIO 4 (with 4.7kΩ pullup)
- GND → Ground

DHT22 Humidity:
- VCC → 3.3V  
- Data → GPIO 22
- GND → Ground
```

## Safety Considerations

⚠️ **IMPORTANT SAFETY WARNINGS**

1. **Electrical Safety**
   - Always disconnect power before wiring
   - Use proper fuses and circuit breakers
   - Ensure proper grounding of all components
   - Never exceed voltage/current ratings

2. **Battery Safety**
   - Use appropriate battery management system (BMS)
   - Monitor temperature and voltage continuously
   - Provide adequate ventilation
   - Follow manufacturer charging guidelines

3. **Thermal Safety**
   - Install thermal protection circuits
   - Monitor component temperatures
   - Provide adequate cooling/heat dissipation
   - Use thermal fuses where appropriate

## Installation Steps

### 1. Prepare Raspberry Pi

```bash
# Flash Raspberry Pi OS to SD card
# Enable SSH and I2C in raspi-config
sudo raspi-config

# Update system
sudo apt update && sudo apt upgrade -y

# Install required libraries
sudo apt install python3-pip git -y
pip3 install RPi.GPIO adafruit-circuitpython-ads1x15
```

### 2. Install Hardware

1. Mount Raspberry Pi in protective case
2. Connect relay module to GPIO pins
3. Wire power sources through relays
4. Install current and voltage sensors
5. Connect temperature sensors
6. Add emergency stop button

### 3. Test Connections

```python
# Test script for hardware verification
import RPi.GPIO as GPIO
import time

# Test relay switching
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)  # Solar relay

for i in range(5):
    GPIO.output(18, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(18, GPIO.LOW)
    time.sleep(1)

GPIO.cleanup()
```

### 4. Calibrate Sensors

1. **Voltage Calibration**
   - Use multimeter to verify voltage readings
   - Adjust voltage divider ratios in software

2. **Current Calibration**
   - Zero current sensors with no load
   - Verify with known current loads

3. **Temperature Calibration**
   - Compare with reference thermometer
   - Apply offset corrections in software

## Troubleshooting

### Common Issues

**Problem**: Relays not switching
- Check GPIO pin assignments
- Verify power supply to relay module
- Test with manual GPIO control

**Problem**: Incorrect sensor readings
- Check wiring connections
- Verify I2C communication
- Test sensors individually

**Problem**: System instability
- Check power supply capacity
- Verify grounding connections
- Monitor for electromagnetic interference

### Testing Commands

```bash
# Test I2C devices
sudo i2cdetect -y 1

# Test GPIO pins
gpio readall

# Monitor system logs
sudo journalctl -f
```

## Performance Optimization

### Power Management
- Use low-power sensors where possible
- Implement sleep modes during low activity
- Optimize reading intervals

### Signal Quality
- Use shielded cables for analog signals
- Implement software filtering
- Add hardware noise reduction

### Reliability
- Include watchdog timers
- Implement error recovery
- Add redundant sensors for critical measurements

## Maintenance

### Regular Checks
- Inspect all connections monthly
- Clean sensors and components
- Check battery health and capacity
- Verify relay operation

### Software Updates
- Keep system software updated
- Monitor for new sensor drivers
- Update AI model as needed

## Support

For hardware support:
- Check the troubleshooting section
- Review wiring diagrams carefully
- Test components individually
- Consult component datasheets

For additional help, open an issue on the GitHub repository.
