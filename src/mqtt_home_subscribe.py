# installed paho-mqtt
from pathlib import Path

from paho.mqtt import client as mqtt_client

import mqtt_settings
from mod_logger import Logger
from remote_ctrl import remote_control

logger_set = Logger("loggerConfig/logConfig.json", Path(__file__).stem)
logger = logger_set.get_log()

broker = mqtt_settings.broker
tcp_port = mqtt_settings.tcp_port
websocket_port = mqtt_settings.websocket_port
tls_ssl_port = mqtt_settings.tls_ssl_port
secure_websocket_port = mqtt_settings.secure_websocket_port
topic = "home/device/command"
clientID = mqtt_settings.subscribe_clientID
user_name = mqtt_settings.user_name
passwd = mqtt_settings.passwd


def on_connect(client, userdata, flags, rc, properties=None):
    # paho 2.0.0の場合、properties パラメータを追加する必要あり
    # def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        logger.info("Connected MQTT Broker!!!")
        # 2026-05-06: 接続完了後に購読する。再接続時も on_connect が呼ばれるため、
        # 切断復帰後に subscribe されない状態を避ける。
        result, mid = client.subscribe(topic, qos=1)
        logger.info(f"Subscribe requested: topic={topic}, result={result}, mid={mid}")
    else:
        logger.info(f"Not Connected MQTT Broker: {rc}")


def on_subscribe(client, userdata, mid, reason_code_list, properties=None):
    # 2026-05-06: subscribe が broker に受理されたかログで確認できるようにする。
    logger.info(f"Subscribed: mid={mid}, reason_codes={reason_code_list}")


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties=None):
    # 2026-05-06: 切断理由をログに残し、受信できない原因を追いやすくする。
    logger.info(f"Disconnected MQTT Broker: {reason_code}")


def connect_mqtt() -> mqtt_client:

    # paho-mqtt 2.0.0 の場合、callback_api_version を設定する必要あり
    client = mqtt_client.Client(
        client_id=clientID, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2
    )

    # TLS/SSL authentication code. one-way
    client.tls_set(ca_certs=mqtt_settings.cert_path)

    # TLS/SSL authentication code. two-way
    # client = mqtt_client.Client(clientID)
    # client.tls_set(
    #     ca_certs="server-ca.crt",
    #     certfile="client.crt",
    #     keyfile="client.key",
    # )

    client.username_pw_set(user_name, passwd)
    # 2026-05-06: MQTT の状態変化と受信処理をログに残すため、callback を明示的に登録する。
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.connect(broker, tls_ssl_port)

    return client


def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    logger.info(f"Received `{payload}` from `{msg.topic}` topic")

    # 2026-05-06: リモコン制御は数値コマンド前提なので、不正 payload はここで止める。
    try:
        value = int(payload)
    except ValueError:
        logger.error(f"Invalid command payload: {payload}")
        return

    # 2026-05-06: I2C や command ファイル読み込みの失敗をログに残す。
    try:
        remote_control(ctrl_num=value)
    except Exception:
        logger.exception(f"Remote control failed: ctrl_num={value}")


# subscribe
def subscribe(client: mqtt_client.Client):
    # 2026-05-06: subscribe は on_connect 側で行う。ここに置くと初回接続前だけの処理になり、
    # 再接続後に購読されない可能性があるため。
    pass


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == "__main__":
    run()
