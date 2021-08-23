# Sample Code for Rasperry Pis
Python code examples for raw sensor communication with many Sensirion sensors.

# Summary
The Raspbberry Pi Platform allows for easy prototyping with endless possibilities. In addition to the documentation in the datasheet and application notes this repository demonstrates the communication with several Sensirion AG sensors through I2C interface which is integrated in Raspberry Pis. The examples are very basic and typically are a starting point for customer specific implementations. The code for the minimal examples only uses the Pyhton based smbus2 library. An installation of Python is needed as well. 

The code for the I2C interface examples is written without the use of abstractions so it could be easily adapted to own projects. To keep the code simple usually no error handling like CRC check or I2C NAK checks are implemented.

# How to use

All samples in this directory share the same format; as such, you can follow the instructions below to get any of them up and running. The code is developed and testet on Raspberry Pi in versions 3B+ and 4B with Raspberry Pi OS Lite. It should work on others versions as well but the scripts needs eventually an adaption like the device number of the i2c interface. Typically the internal pull up resistors are enabled and sufficient so that no additional circuit is needed to operate the sensor on the I2C interface.

The I2C interface is, according to the documentation https://www.raspberrypi.org/documentation/computers/os.html, connected to the pins 3 (SDA) and 5 (SCL). The power supply pins are located at pins 1 (3.3V), 2 (5V) and 6 (GND). Please take care of choosing the correct voltage for the sensor according to the datasheet. If connected to the wrong supply the sensor will be damaged. 

All commands below need to be executed in the console terminal:
1. If not done yet, please follow the documentation how to setup your Raspberry Pi: https://www.raspberrypi.org/documentation/computers/getting-started.html#setting-up-your-raspberry-pi
2. Prepare your Raspberry Pi I2C interface. Activate the I2C interface with executing 
```
sudo raspi-config
```
and navigate to "5 - Interfacing Options" and enable "I2C"
3. Restart the device if necessary
4. . Install additinal software packages
```
sudo apt-get install python3 python3-pip i2c-dev i2c-tools wget
```
4. Install the smbus2 library
```
pip3 install smbus2
```
5. Retrieve this example file from github, please adapt the link below according to the script you would like to use
```
wget -L https://raw.githubusercontent.com/Fototux/python_snippets_for_raspberry_pi/main/sensor_script.py
```
6. Shutdown the Raspbery Pi to prevent any short circuits while handling and connect the sensor to the I2C interface
```
sudo shutdown -h now
```
7. Check if the sensor is detected on the I2C bus
```
i2cdetect -y 1
```
should result in 
the result should look like this for an sensor on address 0x2e:
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- 2e -- 
```
If the sensor is not detected, check your wiring and if the correct voltage supply is used. 
8. Run the example, please adapt the naming of the script according to your sensor
```
python3 sensor_script.py
```

