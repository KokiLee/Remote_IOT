# Install Mosquitto MQTT

```bash
sudo apt install mosquitto
```

## Start Mosquitto MQTT

```bash
sudo systemctl start mosquitto
```

## Stop Mosquitto MQTT

```bash
sudo systemctl stop mosquitto
```

## Enable Mosquitto MQTT

```bash
sudo systemctl enable mosquitto
```

## Disable Mosquitto MQTT

```bash
sudo systemctl disable mosquitto
```

## Restart Mosquitto MQTT

```bash
sudo systemctl restart mosquitto
```

## Check Mosquitto MQTT status

```bash
sudo systemctl status mosquitto
```

## User Certificate

はじめてユーザーを追加する時は、

```bash
sudo mosquitto_passwd -c /etc/mosquitto/passwd usernam
```

2番目以降のユーザーを追加する時は、-cをつけない

```bash
sudo mosquitto_passwd /etc/mosquitto/passwd username
```

### check password

```bash
cat /etc/mosquitto/pwfile
```

Passwordはハッシュ値で保存されます。

### Create root CA, server CA, server key, server cert

```bash
# フォルダ作成
mkdir certs
cd certs
# パスフレーズの入力を求められる。入力しないと次に進めない、入力内容は保存する。
openssl genrsa -des3 -out root-ca.key 2048

# 証明書作成に必要なca.csrファイルを作成する
openssl req -new -key root-ca.key -out root-ca.csr -sha256

# 所属などを聞かれるので入力する
# Common Name に注意。こちらはサーバ側とは違う値を入力する。サーバ側はドメイン名

# Country name: JP
# State or Province nam: IOT
# Locality name: home
# Organization name: Factory
# Organization UnitName: Develop
# Common Name: home_iot
# Email: mqtt@mqtt.com
# A challenge password: 
# An optional campany name: 

# ルート証明書(CA.crt)を作成する
openssl x509 -req -in root-ca.csr -signkey root-ca.key -out root-ca.crt -days 36500 -sha256

# サーバー証明書(server.crt)を作成する
openssl genrsa -out server.key 2048

# サーバー証明書(server.csr)を作成する
openssl req -new -key server.key -out server.csr -sha256

# 所属をきかれるので入力する
# Common NameはルートCA側とは異なる値を入力する。サーバ側なのでドメイン名を入力

# Country name: JP
# State or Province nam: myEC2
# Locality name: web
# Organization name: IOT
# Organization UnitName: Home
# Common Name: website.org
# Email: mqtt@mqtt.com
# A challenge password: 
# An optional campany name: 

# サーバー証明書(server.crt)を作成する
openssl x509 -req -in server.csr -CA root-ca.crt -CAkey root-ca.key -CAcreateserial -out server.crt -days 36500 -sha256

# 生成したファイルの権限確認
ls -lh

-rw-rw-r-- 1 ubuntu ubuntu 1.3K Aug 15 22:23 server.crt
-rw-r--r-- 1 ubuntu ubuntu 1.7K Aug 15 22:20 server.key
-rw-r--r-- 1 root   root   1.3K Aug 15 21:35 root-ca.crt

# server.keyの権限を変更。※-rw-------の場合mosquittoが起動しない
chmod 644 server.key

# 作成したファイルをサーバの /etc/mosquitto/certsにコピー

```

### mosquitto.conf

```bash
sudo nano /etc/mosquitto/mosquitto.conf
```

confファイルを設定する

```text
# Place your local configuration in /etc/mosquitto/conf.d/
#
# A full description of the configuration file is at
# /usr/share/doc/mosquitto/examples/mosquitto.conf.example

pid_file /run/mosquitto/mosquitto.pid

persistence true
persistence_location /var/lib/mosquitto/

log_dest file /var/log/mosquitto/mosquitto.log

include_dir /etc/mosquitto/conf.d

# additional point

# enable user certification
# only connect user
allow_anonymous false # ユーザー認証を使用する場合はfalseにする

# password file
password_file /etc/mosquitto/pwfile # ユーザー認証を使用する場合はパスワードファイルのパスを指定する

# enable TLS
listener 8883 # ポート番号を指定する default

# cert file path 証明書のパスを指定する
cafile   /etc/mosquitto/certs/root-ca.crt 
certfile /etc/mosquitto/certs/server.crt
keyfile  /etc/mosquitto/certs/server.key
```

### mosquittoを再起動する

```bash
sudo systemctl restart mosquitto
sudo systemctl status mosquitto
```

## Test code

publishする。localからサーバへデータを送信する。

```bash
mosquitto_pub -h <ドメイン> -p 8883 -t "topic" -m "message" -u <username> -P <password> --cafile ./root-ca.crt
```

publishされたデータをサーバ側でsubscribe。

```bash
mosquitto_sub -h <ドメイン> -p 8883 -t "topic" -u <username> -P <password> --cafile /etc/mosquitto/certs/root-ca.crt
```

## 備考

今回は、AWS EC2にMQTTBrokerを立てて、Raspberry Piからデータを送信。(温湿度データ)
WEBサイトのFormからデータをPublish、Raspberry PiからデータをSubscribeして、データを取得して
家電のON,OFFを制御する用途でMQTTを使用しました。
