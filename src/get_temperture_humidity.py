# adafruit/Adafruit_CircuitPython_DHT/examples/dht_simpletest.py
# Lines 1 to 35 in main

# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time

import board

import adafruit_dht
import json
import os
from logging import getLogger, config

# logger
with open("loggerConfig/logConfig.json") as f:
    config_json = json.load(f)

script_name = os.path.splitext(os.path.basename(__file__))[0]

# dynamic log-file name
config_json["handlers"]["file"]["filename"] = f"log/{script_name}.log"

config.dictConfig(config_json)
logger = getLogger(__name__)

# Initial the dht device, with data pin connected to:
# change one-wire-gpio 18 to 26
dhtDevice = adafruit_dht.DHT22(board.D26, use_pulseio=False)

# you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
# This may be necessary on a Linux single board computer like the Raspberry Pi,
# but it will not work in CircuitPython.
# dhtDevice = adafruit_dht.DHT22(board.D18, use_pulseio=False)


def get_temperture():
    try:
        temperature_c = dhtDevice.temperature
        logger.info(f"Celsius = {temperature_c}")
        return temperature_c
    except RuntimeError as e:
        logger.error(e.args[0])
    except Exception as e:
        dhtDevice.exit()
        logger.error(e)
        raise e


def get_humidity():
    try:
        humidity = dhtDevice.humidity
        logger.info(f"Humidity = {humidity}")
        return humidity
    except RuntimeError as e:
        logger.error(e.args[0])
    except Exception as e:
        dhtDevice.exit()
        logger.error(e)
        raise e


if __name__ == "__main__":
    print(get_temperture())
    print(get_humidity())

# while True:
#     try:
#         # Print the values to the serial port
#         temperature_c = dhtDevice.temperature
#         temperature_f = temperature_c * (9 / 5) + 32 # Convert Celesous to Fahrenheit
#         humidity = dhtDevice.humidity
#         print(
#             f"Temp: {temperature_f:.1f} F / {temperature_c:.1f} C    Humidity: {humidity}% "
#         )

#     except RuntimeError as error:
#         # Errors happen fairly often, DHT's are hard to read, just keep going
#         print(error.args[0])
#         time.sleep(2.0)
#         continue
#     except Exception as error:
#         dhtDevice.exit()
#         raise error

#     time.sleep(2.0)
