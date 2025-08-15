# How to use Raspberry Pi Camera

## System

- ハードウェア
  - Raspberry Pi 4 Model B Rev 1.5(.venv)
  - DHT22

```bash
cat /proc/device-tree/model
# Raspberry Pi 4 Model B Rev 1.5(.venv)
```

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

```bash
sudo apt update
sudo apt install libcamera_apps
```

## config.txt

```bash
sudo nano /boot/firmware/config.txt

# 最後に以下を追加
dtoverlay=imx219
```

## Use Camera

```bash
rpicam-still -o test.jpg
```

### Camera command

```bash
# 中央2倍拡大
rpicam-still -o zoom.jpg --roi 0.25,0.25,0.5,0.5 # x,y,w,h

# 動画撮影
rpicam-vid -t 10000 -o video.h264 # 10秒間撮影
```

[RasberryPi]([text](https://www.raspberrypi.com/documentation/computers/camera_software.html))

> Raspberry Pi OS Bookworm は、カメラキャプチャアプリケーションの名前を から に変更しましたlibcamera-
> *。rpicam-*シンボリックリンクを使用すると、今のところは古い名前を使用できます。新しいアプリケーション名を
> できるだけ早く採用してください。Bookwormより前のバージョンの Raspberry Pi OS では、このlibcamera-*
> 名前が引き続き使用されています。

とのこと。
