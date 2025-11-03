# adafruit/Adafruit_CircuitPython_DHT/examples/dht_simpletest.py
# Lines 1 to 35 in main

# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
from pathlib import Path

import adafruit_dht
import board

from mod_logger import Logger

logger_set = Logger("loggerConfig/logConfig.json", Path(__file__).stem)
logger = logger_set.get_log()

# Initial the dht device, with data pin connected to:
dhtDevice = adafruit_dht.DHT22(board.D26, use_pulseio=False)

# you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
# This may be necessary on a Linux single board computer like the Raspberry Pi,
# but it will not work in CircuitPython.
# dhtDevice = adafruit_dht.DHT22(board.D18, use_pulseio=False)

previous_temp = 0.0


def get_temperture():
    global previous_temp
    try:
        temperature_c = dhtDevice.temperature
        logger.info(f"Celsius = {temperature_c}")
        if temperature_c > previous_temp + 10.0 and previous_temp != 0.0:
            temperature_c = previous_temp
        previous_temp = temperature_c
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
    try:
        while True:
            get_temperture()
            get_humidity()

            time.sleep(3)
    except KeyboardInterrupt:
        logger.info("Finish")
    except Exception as error:
        dhtDevice.exit()
        raise error
    finally:
        dhtDevice.exit()
