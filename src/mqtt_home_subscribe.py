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
    else:
        logger.info(f"Not Connected MQTT Broker: {rc}")


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
    client.on_connect = on_connect
    client.connect(broker, tls_ssl_port)

    return client


def on_message(client, userdata, msg):
    logger.info(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    value = int(msg.payload.decode())

    remote_control(ctrl_num=value)


# subscribe
def subscribe(client: mqtt_client.Client):

    client.subscribe(topic, qos=1)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == "__main__":
    run()
