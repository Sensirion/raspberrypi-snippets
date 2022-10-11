#!/usr/bin/python
#
# Copyright (c) 2022, Sensirion AG
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

# Example to use a Sensirion SEN55 with a Raspbery Pi
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
# 60: -- -- -- -- -- -- -- -- -- 69 -- -- -- -- -- --
# 70: -- -- -- -- -- -- -- --
#
# - Retrieve this example file from github
# 'wget -L URL'
#
# - Run the example 'python3 SEN5x_I2C_minimal_example.py.py'

import time
from smbus2 import SMBus, i2c_msg
from struct import unpack

def CrcCalculator(data):
    """
        Constructs a calculator object with the given CRC parameters.
        :param int width:
            Number of bits of the CRC (e.g. 8 for CRC-8).
        :param int polynomial:
            The polynomial of the CRC, without leading '1' (e.g. 0x31 for the
            polynomial x^8 + x^5 + x^4 + 1).
        :param int init_value:
            Initialization value of the CRC. Defaults to 0.
        :param int final_xor:
            Final XOR value of the CRC. Defaults to 0.
    """
    width = 8
    polynomial = 0x31
    final_xor = 0x00
    crc = 0xFF
    for value in data:
        crc ^= value
        for i in range(width):
            if crc & (1 << (width - 1)):
                crc = (crc << 1) ^ polynomial
            else:
                crc = crc << 1
            crc &= (1 << width) - 1
    return crc ^ final_xor

# I2C bus 1 on a Raspberry Pi 3B+
# SDA on GPIO2=Pin3 and SCL on GPIO3=Pin5
# sensor +3.3V at Pin1 and GND at Pin6
DEVICE_BUS = 1

# device address SEN55
DEVICE_ADDR = 0x69

# init I2C
bus = SMBus(DEVICE_BUS)

# wait 1 s for sensor start up (> 1000 ms according to datasheet)
time.sleep(1)

#Read status of the STAR engine
msg = i2c_msg.write(DEVICE_ADDR, [0x60, 0xB2])
bus.i2c_rdwr(msg)

# wait 10 ms for data ready
time.sleep(0.01)

# read 9 bytes in as a sequence of MSB, LSB, CRC
# offset, slope. time constant
msg = i2c_msg.read(DEVICE_ADDR, 9)
bus.i2c_rdwr(msg)

# merge byte 0 and byte 1 to integer
t_offset  = int(unpack(">h", msg.buf[0:2])[0]) #different method choosen here due to the possible negative sign in parameter
t_slope  = (msg.buf[3][0] << 8 | msg.buf[4][0])
t_time  = (msg.buf[6][0] << 8 | msg.buf[7][0])

print("Preset T Offset: "+str(t_offset/200))
print("Preset Slope: "+str(t_slope/10000))
print("Preset Time Constant: "+str(t_time))

# wait 10 ms for data ready
time.sleep(0.01)

#Set new values:
t_offset = int(-5 * 200)
t_slope = int(0.01 * 10000)
t_time = int(10 * 60)

data = []
data.append((t_offset & 0xff00) >> 8)
data.append(t_offset & 0x00ff)

data.append((t_slope & 0xff00) >> 8)
data.append(t_slope & 0x00ff)

data.append((t_time & 0xff00) >> 8)
data.append(t_time & 0x00ff)

msg = i2c_msg.write(
  DEVICE_ADDR,
  [0x60, 0xB2,
  data[0], data[1], CrcCalculator(data[0:2]),
  data[2], data[3], CrcCalculator(data[2:4]),
  data[4], data[5], CrcCalculator(data[4:6])]
)
bus.i2c_rdwr(msg)

# wait 10 ms for data ready
time.sleep(0.01)

#Read status of the STAR engine
msg = i2c_msg.write(DEVICE_ADDR, [0x60, 0xB2])
bus.i2c_rdwr(msg)

# wait 10 ms for data ready
time.sleep(0.01)

# read 3 bytes in as a sequence of MSB, LSB, CRC
# status
msg = i2c_msg.read(DEVICE_ADDR, 9)
bus.i2c_rdwr(msg)

# merge byte 0 and byte 1 to integer
t_offset = int(unpack(">h", msg.buf[0:2])[0]) #different method choosen here due to the possible negative sign in parameter
t_slope = (msg.buf[3][0] << 8 | msg.buf[4][0])
t_time = (msg.buf[6][0] << 8 | msg.buf[7][0])

print("Preset T Offset: "+str(t_offset/200))
print("Preset Slope: "+str(t_slope/10000))
print("Preset Time Constant: "+str(t_time))

# wait 10 ms for data ready
time.sleep(0.01)

# start scd measurement in periodic mode, will update every 2 s
msg = i2c_msg.write(DEVICE_ADDR, [0x00, 0x21])
bus.i2c_rdwr(msg)

# wait for first measurement to be finished
time.sleep(2)

# repeat read out of sensor data
print("pm1p0 \t pm2p5 \t pm4p0 \t pm10p0\t voc \t nox \t temperature \t humidity")
for i in range(1000):
    msg = i2c_msg.write(DEVICE_ADDR, [0x03, 0xC4])
    bus.i2c_rdwr(msg)

    # wait 1 ms for data ready
    time.sleep(0.001)

    # read 12 bytes; each three bytes in as a sequence of MSB, LSB, CRC
    # co2, temperature, rel. humidity, status
    msg = i2c_msg.read(DEVICE_ADDR, 24)
    bus.i2c_rdwr(msg)

    # merge byte 0 and byte 1 to integer
    # co2 is in ppm
    pm1p0 = (msg.buf[0][0] << 8 | msg.buf[1][0])/10
    pm2p5 = (msg.buf[3][0] << 8 | msg.buf[4][0])/10
    pm4p0 = (msg.buf[6][0] << 8 | msg.buf[7][0])/10
    pm10p0 = (msg.buf[9][0] << 8 | msg.buf[10][0])/10

    # merge byte 3 and byte 4 to integer
    temperature = msg.buf[15][0] << 8 | msg.buf[16][0]
    # calculate temperature  according to datasheet
    temperature /= 200

    # merge byte 6 and byte 7 to integer
    humidity = msg.buf[12][0] << 8 | msg.buf[13][0]
    # calculate relative humidity according to datasheet
    humidity /= 100

    voc = (msg.buf[18][0] << 8 | msg.buf[19][0]) / 10
    nox = (msg.buf[21][0] << 8 | msg.buf[22][0]) / 10

    print("{:.2f} \t {:.2f} \t {:.2f} \t {:.2f} \t {:.0f} \t {:.0f} \t {:.2f} \t\t {:.2f}".format(pm1p0, pm2p5, pm4p0, pm10p0, voc, nox, temperature, humidity))

    # wait 2 s for next measurement
    time.sleep(2)



bus.close()
