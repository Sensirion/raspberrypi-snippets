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
# (c) Copyright 2020 Sensirion AG, Switzerland

# Example to use a Sensirion SD20 with a Raspbery Pi
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
# executing the command 'i2cdetect -q 1'
# WARNING -> use the parameter "-q" with caution, it may damage your system
# this parameter is known to potenitially corrupt some EEPROMS like Atmel AT24RF08
# the result should look like this:
#      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
# 00:          -- -- -- -- -- 08 -- -- -- -- -- -- -- 
# 10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
# 20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
#
# - Retrieve this example file from github
# 'wget -L https://raw.githubusercontent.com/Sensirion/raspberrypi-snippets/main/LD20_I2C_minmal_example.py'
#
# - Run the example 'python3 ld20.py'

import time
from smbus2 import SMBus, i2c_msg

# I2C bus 1 on a Raspberry Pi 3B+
# SDA on GPIO2=Pin3 and SCL on GPIO3=Pin5
# sensor +3.3V at Pin1 and GND at Pin6
DEVICE_BUS = 1

# device address LD20
DEVICE_ADDR = 0x08

# init I2C
bus = SMBus(DEVICE_BUS)

#wait 1 s for sensor start up (> 25 ms according to datasheet)
time.sleep(1)

# scale factors needed to convert sensor flow raw data
# from datasheet section 4.5.1 (scale_flow = 1200, scale_temprature = 200)
SCALE_FACTOR_FLOW = 1200.0
SCALE_FACTOR_TEMP = 200.0


# send start continuous measurement command to the sensor  (0x3608)
# start in continuous mode for H2O
msg = i2c_msg.write(DEVICE_ADDR, [0x36, 0x08])
bus.i2c_rdwr(msg)

# repeat read out of sensor data
for i in range(10):
    # wait for  first measurement for 12 ms + 150 ms warm up for highest accuracy
    # after first measurement update rate can be set to a higher value
    time.sleep(1)
    # read 9 bytes, MSB, LSB, CRC -> flow, temperature, flags
    msg = i2c_msg.read(DEVICE_ADDR, 6)
    bus.i2c_rdwr(msg)
    # merge byte 0 and byte 1 to integer
    flow_raw = msg.buf[0][0]<<8 | msg.buf[1][0]
    # convert from unsigned to signed
    flow_raw = flow_raw if flow_raw < (1 << 16-1) else flow_raw - (1 << 16)

    # calculate flow according to datasheet section 4.5.2
    flow = flow_raw / SCALE_FACTOR_FLOW

    # merge byte 3 and byte 4 to integer
    temperature = msg.buf[3][0]<<8 | msg.buf[4][0]
    # calculate temperature  according to sectino 4.5.3 in the datasheet
    temperature = temperature / SCALE_FACTOR_TEMP
    print("{:.2f},{:.2f}".format(flow, temperature))

# stop the measurement
# if measurement has not been stopped,
# sending the start command again will result in i2c error
msg = i2c_msg.write(DEVICE_ADDR, [0x3F, 0xF9])
bus.i2c_rdwr(msg)

bus.close()


