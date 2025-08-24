# RemoteIOT

Raspberry Piを使用したIoTリモート制御システムです。MQTTプロトコルを通じて、温度・湿度センサー、カメラ、赤外線リモコンなどのデバイスを制御・監視できます。

## 概要

このプロジェクトは、Raspberry Piを中心としたIoTシステムで、以下の機能を提供します：

- **環境監視**: DHT22センサーによる温度・湿度の測定
- **リモート制御**: 赤外線リモコンによる家電制御
- **画像取得**: Raspberry Piカメラによる画像キャプチャ
- **MQTT通信**: セキュアなTLS/SSL通信によるデータ送受信
- **ログ管理**: 包括的なログシステム

## 機能

### 🔍 センサー監視
- **温度・湿度センサー (DHT22)**: GPIO26に接続されたDHT22センサーで環境データを取得
- **CPU温度監視**: Raspberry PiのCPU温度を監視
- **自動データ送信**: 定期的にMQTTブローカーにセンサーデータを送信

### 📷 カメラ機能
- **自動撮影**: 1分間隔で画像を自動撮影
- **日付別整理**: 撮影した画像を日付別フォルダに自動整理
- **画像処理**: 上下反転処理による正しい向きでの保存

### 🎮 リモート制御
- **赤外線リモコン**: 学習リモコン基板(ADRSIR)を使用した家電制御
- **コマンドベース**: 読み込み、書き込み、送信の各操作に対応

### 📡 MQTT通信
- **セキュア通信**: TLS/SSL認証による安全な通信
- **自動再接続**: 接続が切れた場合の自動再接続機能
- **双方向通信**: データ送信とコマンド受信の両方をサポート

## システム要件

### ハードウェア
- Raspberry Pi (推奨: Raspberry Pi 4)
- DHT22温度・湿度センサー
- Raspberry Piカメラモジュール
- 学習リモコン基板 (ADRSIR)

### ソフトウェア
- Python 3.7+
- Raspberry Pi OS (推奨: Bullseye以降)

## インストール

### 1. リポジトリのクローン
```bash
git clone <repository-url>
cd RemoteIOT
```

### 2. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 3. システムパッケージのインストール
```bash
sudo apt update
sudo apt install python3-picamera2
```

### 4. 設定ファイルの準備
`mqtt_settings.py`ファイルを作成し、MQTTブローカーの設定を行ってください：

```python
# mqtt_settings.py の例
broker = "your-mqtt-broker.com"
tcp_port = 1883
websocket_port = 8080
tls_ssl_port = 8883
secure_websocket_port = 8081
topic = "home/sensor/data"
clientID = "your-client-id"
subscribe_clientID = "your-subscribe-client-id"
user_name = "your-username"
passwd = "your-password"
cert_path = "path/to/your/ca.crt"
```

## 使用方法

### センサーデータの送信
```bash
python3 src/mqtt_home_publish.py
```

### コマンドの受信・実行
```bash
python3 src/mqtt_home_subscribe.py
```

### カメラ撮影
```bash
python3 src/rpi_camera.py
```

### 温度・湿度の測定
```bash
python3 src/get_temperture_humidity.py
```

### リモコン制御
```bash
python3 src/remote_ctrl.py
```

## プロジェクト構造

```
RemoteIOT/
├── src/                          # メインソースコード
│   ├── mqtt_home_publish.py     # MQTTデータ送信
│   ├── mqtt_home_subscribe.py   # MQTTコマンド受信
│   ├── remote_ctrl.py           # 赤外線リモコン制御
│   ├── rpi_camera.py            # カメラ制御
│   ├── get_temperture_humidity.py # 温湿度センサー
│   ├── get_raspi_temp.py        # CPU温度取得
│   ├── usb_camera.py            # USBカメラ制御
│   ├── mod_logger.py            # ログ管理
│   └── mqtt_settings.py         # MQTT設定
├── loggerConfig/                 # ログ設定ファイル
├── log/                          # ログファイル
├── images/                       # 撮影画像保存
├── requirements.txt              # Python依存関係
└── README.md                     # このファイル
```

## 設定

### GPIO設定
- **DHT22**: GPIO26
- **カメラ**: 標準Raspberry Piカメラインターフェース
- **リモコン基板**: I2C (SDA: GPIO2, SCL: GPIO3)

### MQTT設定
- **トピック**: `home/device/command` (受信), `home/sensor/data` (送信)
- **QoS**: 1 (受信), 0 (送信)
- **認証**: TLS/SSL + ユーザー名/パスワード

## ログ

システムは包括的なログ機能を提供します：
- 各スクリプトの実行ログ
- エラーと警告の記録
- センサーデータの記録
- MQTT通信の状態記録

ログファイルは `log/` ディレクトリに保存され、スクリプト名別に管理されます。

## トラブルシューティング

### よくある問題

1. **DHT22センサーが動作しない**
   - GPIO26の接続を確認
   - 電源供給を確認

2. **カメラが動作しない**
   - `sudo raspi-config` でカメラを有効化
   - カメラモジュールの接続を確認

3. **MQTT接続エラー**
   - ネットワーク接続を確認
   - 証明書ファイルのパスを確認
   - ユーザー名・パスワードを確認

4. **リモコンが動作しない**
   - I2Cが有効化されているか確認
   - Arduinoとの接続を確認

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

プロジェクトへの貢献を歓迎します。以下の方法で貢献できます：

1. イシューの報告
2. プルリクエストの送信
3. ドキュメントの改善
4. 新機能の提案

## 更新履歴

- **v1.0**: 初期リリース
  - MQTT通信機能
  - センサー監視機能
  - カメラ機能
  - リモコン制御機能

---

**注意**: このシステムを使用する前に、適切なセキュリティ設定を行い、ネットワーク環境に合わせた設定を行ってください。
