# installed paho-mqtt
import time
from pathlib import Path

from paho.mqtt import client as mqtt_client

import mqtt_settings
from mod_logger import Logger

logger_set = Logger("loggerConfig/logConfig.json", Path(__file__).stem)
logger = logger_set.get_log()

broker = mqtt_settings.broker
tcp_port = mqtt_settings.tcp_port
websocket_port = mqtt_settings.websocket_port
tls_ssl_port = mqtt_settings.tls_ssl_port
secure_websocket_port = mqtt_settings.secure_websocket_port
topic = mqtt_settings.topic
clientID = mqtt_settings.clientID
user_name = mqtt_settings.user_name
passwd = mqtt_settings.passwd


# 自動再接続
FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60
FLAG_EXIT = False


def on_connect(client, userdata, flags, rc, properties=None):
    # paho 2.0.0の場合、properties パラメータを追加する必要あり
    # def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        logger.info("Connected MQTT Broker!!!")
    else:
        logger.info(f"Not Connected MQTT Broker: {rc}")


def connect_mqtt():
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
    client.connect(broker, tls_ssl_port, keepalive=60)

    return client


def on_disconnect(client, userdata, rc, properties=None, *args):
    logger.info("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        logger.info("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            logger.info("Reconnected successfully!")
            return
        except Exception as err:
            logger.error("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    logger.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)
    global FLAG_EXIT
    FLAG_EXIT = True


def publish_command(topic, payload, qos):
    client = connect_mqtt()
    client.loop_start()

    res = client.publish(topic=topic, payload=payload, qos=qos)
    logger.info(f"publish topic & message: {topic}, {payload}")

    res.wait_for_publish()

    if res.is_published():
        client.disconnect()
        logger.info("Disconnected")


if __name__ == "__main__":
    publish_command(topic="home/device/command", payload=10, qos=1)
