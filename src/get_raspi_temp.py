import subprocess
from pathlib import Path

from mod_logger import Logger

logger_set = Logger("loggerConfig/logConfig.json", Path(__file__).stem)
logger = logger_set.get_log()


def get_cpu_temperture():
    try:
        result = subprocess.run(
            ["vcgencmd", "measure_temp"], capture_output=True, text=True, check=True
        )

        temp_str = result.stdout.strip()
        temp_value = float(temp_str.replace("temp=", "").replace("'C", ""))

        return temp_value

    except subprocess.CalledProcessError as e:
        logger.error(f"Commadn Error: {e}")
        return None
    except ValueError as e:
        logger.error(f"Data Analysis Error: {e}")
        return None


if __name__ == "__main__":
    logger.info(f"CPU TEMP {get_cpu_temperture()}")
