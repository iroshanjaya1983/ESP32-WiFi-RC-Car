# 🏎️ ESP32 WiFi RC Car (MicroPython)

A DIY Remote Controlled car using an ESP32, L298N motor driver, and a mobile-friendly web dashboard.

## [cite_start]🛠️ Hardware Requirements [cite: 1]
* [cite_start]**NodeMCU ESP32** [cite: 1]
* [cite_start]**L298N Motor Driver** [cite: 1]
* [cite_start]**2x DC Motors** & **2WD Chassis** [cite: 1]
* [cite_start]**7.4v Li-ion** or **6v AA Battery Pack** [cite: 1, 2]

## [cite_start]🔌 Wiring [cite: 11]
| L298N | ESP32 Pin | Function |
| :--- | :--- | :--- |
| IN1 | D1 (GPIO5) | [cite_start]Left Motor [cite: 11] |
| IN2 | D2 (GPIO4) | [cite_start]Left Motor [cite: 12] |
| ENA | D5 (GPIO14)| [cite_start]Left Speed (PWM) [cite: 12] |
| 5V | VIN | [cite_start]Power NodeMCU  |
| GND | GND | [cite_start]Common Ground  |

## [cite_start]🚀 Getting Started [cite: 3]
1. [cite_start]**Flash MicroPython:** Use `esptool` to erase and flash the ESP32. [cite: 3]
2. [cite_start]**Upload Code:** Use Thonny IDE or `ampy` to save `main.py` to the device. [cite: 3]
3. [cite_start]**Connect:** Power the car, join the WiFi **RC-Car-ESP32** (Password: `12345678`). [cite: 3]
4. [cite_start]**Control:** Open `http://192.168.4.1` in your browser! [cite: 3]
