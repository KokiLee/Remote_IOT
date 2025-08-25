# raspiに apt install python3-picamera2
import time
from datetime import datetime
from pathlib import Path

from picamera2 import Picamera2
from PIL import Image

from mod_logger import Logger

logger_set = Logger("loggerConfig/logConfig.json", Path(__file__).stem)
logger = logger_set.get_log()

dir_date_path = datetime.now().strftime("%Y%m%d")

config_dir = Path.home() / "RemoteIOT" / "images"

# instance
picam2 = Picamera2()
config = picam2.create_still_configuration(
    main={"size": (640, 400), "format": "BGR888"}
)

cameras = picam2.global_camera_info()
logger.info(f"Available cameras: {cameras}")

picam2.configure(config)

picam2.start()


def capture():
    img = None
    try:
        image_array = picam2.capture_array()
        img = Image.fromarray(image_array)
        img = img.transpose(method=Image.FLIP_TOP_BOTTOM)  # upside down

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        image_dir = Path(config_dir / f"images_{date_comparison(dir_date_path)}")
        image_dir.mkdir(parents=True, exist_ok=True)

        file_path = make_date_path(image_dir, timestamp, name="photo")

        img.save(file_path)
        logger.info(f"save photo: {file_path}")
    except Exception as e:
        logger.error(f"don't save photo: {e}")
    finally:
        if img:
            del img
        del image_array


def get_current_date():
    return datetime.now().strftime("%Y%m%d")


def date_comparison(current_date):
    if current_date != get_current_date():
        return datetime.now().strftime("%Y%m%d")
    else:
        return current_date


def make_date_path(dir_path, timestamp, name):
    return dir_path / f"{name}_{timestamp}.jpg"


if __name__ == "__main__":
    try:
        while True:

            capture()

            time.sleep(60)
    except KeyboardInterrupt:
        print("finish")
    finally:
        picam2.stop()
