# Use DHT22

## システム環境

- ハードウェア
  - Raspberry Pi 4 Model B Rev 1.5(.venv)
  - DHT22

```bash
cat /etc/os-release
```

> PRETTY_NAME="Debian GNU/Linux 12 (bookworm)"
> NAME="Debian GNU/Linux"
> VERSION_ID="12"
> VERSION="12 (bookworm)"
> VERSION_CODENAME=bookworm
> ID=debian
> HOME_URL="https://www.debian.org/"
> SUPPORT_URL="https://www.debian.org/support"
> BUG_REPORT_URL="https://bugs.debian.org/"

## Install packages

仮想環境を作成
```bash
# system-site-packagesを使用すると、システムのパッケージを使用することができる。
python -m venv .venv --system-site-packages
```

仮想環境を有効化
```bash
source .venv/bin/activate
```

パッケージをインストール
```bash
pip install adafruit-circuitpython-dht
```

## Use DHT22

```python
import board
import adafruit_dht

from logging import getLogger, config

# logger
with open("loggerConfig/logConfig.json") as f:
    config_json = json.load(f)

script_name = os.path.splitext(os.path.basename(__file__))[0]

# dynamic log-file name
config_json["handlers"]["file"]["filename"] = f"log/{script_name}.log"

config.dictConfig(config_json)
logger = getLogger(__name__)

# デフォルトのPINを使用していたので、ピンを指定する。
dht_device = adafruit_dht.DHT22(board.D26, use_pulseio=False)

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
```