#!/usr/bin/python
#
# Copyright (c) 2020, Sensirion AG
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# # Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# # Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# # Neither the name of Sensirion AG nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# (c) Copyright 2021 Sensirion AG, Switzerland

# Example to use a Sensirion SCD40 or SCD41 with a Raspbery Pi
# 
# Prerequisites: 
#
# - open the command line tool
#
# - Enable the i2c interface on your Raspbery Pi
# using 'sudo raspi-config'
#
# - Install python3 and pip3 and some tools
# 'sudo apt-get install python3 python3-pip i2c-dev i2c-tools wget'
#
# - Install the smbus2 library
# 'pip3 install smbus2'
#
# - Check if the sensor is recognized on the i2c bus
# executing the command 'i2cdetect -y 1'
# the result should look like this:
#      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
# 00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
# 10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
# 20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
# 30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
# 40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
# 50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
# 60: -- -- 62 -- -- -- -- -- -- -- -- -- -- -- -- -- 
#
# - Retrieve this example file from github
# 'wget -L https://raw.githubusercontent.com/Sensirion/raspberrypi-snippets/main/LD20_I2C_minmal_example.py'
#
# - Run the example 'python3 SCD4x_I2C_PYTHON_minmal_example.py'

import time
from smbus2 import SMBus, i2c_msg

# I2C bus 1 on a Raspberry Pi 3B+
# SDA on GPIO2=Pin3 and SCL on GPIO3=Pin5
# sensor +3.3V at Pin1 and GND at Pin6
DEVICE_BUS = 1

# device address SCD4x
DEVICE_ADDR = 0x62

# init I2C
bus = SMBus(DEVICE_BUS)

# wait 1 s for sensor start up (> 1000 ms according to datasheet)
time.sleep(1)

# start scd measurement in periodic mode, will update every 5 s
msg = i2c_msg.write(DEVICE_ADDR, [0x21, 0xB1])
bus.i2c_rdwr(msg)

# wait for first measurement to be finished
time.sleep(5)

# repeat read out of sensor data
for i in range(10):

    msg = i2c_msg.write(DEVICE_ADDR, [0xEC, 0x05])
    bus.i2c_rdwr(msg)

    # wait 1 ms for data ready
    time.sleep(0.001)

    # read 12 bytes; each three bytes in as a sequence of MSB, LSB, CRC
    # co2, temperature, rel. humidity, status
    msg = i2c_msg.read(DEVICE_ADDR, 12)
    bus.i2c_rdwr(msg)
    
    # merge byte 0 and byte 1 to integer
    # co2 is in ppm
    co2 = msg.buf[0][0]<<8 | msg.buf[1][0]

    # merge byte 3 and byte 4 to integer
    temperature = msg.buf[3][0]<<8 | msg.buf[4][0]
    # calculate temperature  according to datasheet
    temperature = -45 + 175 * (temperature) / 65536.
    
    # merge byte 6 and byte 7 to integer
    humidity = msg.buf[6][0]<<8 | msg.buf[7][0]
    # calculate relative humidity according to datasheet
    humidity = 100 * (humidity) / 65536.
        
    print("{:.2f},{:.2f},{:.2f}".format(co2, temperature, humidity))

    # wait 5 s for next measurement
    time.sleep(5)

# stop the measurement
# sensor will go to idle mode
msg = i2c_msg.write(DEVICE_ADDR, [0x3F, 0x86])
bus.i2c_rdwr(msg)
    
# wait 500 ms for finish command
time.sleep(0.5)
    
bus.close()

