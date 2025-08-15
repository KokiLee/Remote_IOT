import json
from logging import config, getLogger
from pathlib import Path


class Logger:
    def __init__(self, config_file, script_name):
        if config_file is None:
            self.config_path = (
                Path(__file__).parent.parent / "loggerConfig" / "logConfig.json"
            )
        else:
            self.config_path = Path(config_file)

        self.script_name = script_name
        self.configured = False

    def configure(self):
        try:
            with open(self.config_path) as f:
                config_json = json.load(f)

            log_dir = Path(__file__).parent.parent / "log"
            config_json["handlers"]["file"]["filename"] = str(
                log_dir / f"{self.script_name}.log"
            )

            config.dictConfig(config_json)
            self.configured = True

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"File is not Json type: {e}")

    def get_log(self):
        if not self.configured:
            self.configure()

        return getLogger(__name__)


if __name__ == "__main__":
    log_class = Logger(
        config_file="loggerConfig/logConfig.json", script_name=Path(__file__).stem
    )

    logger = log_class.get_log()

    logger.info("test")
