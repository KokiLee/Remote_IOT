# Install Mosquitto MQTT

```bash
sudo apt-get install mosquitto
```

# Start Mosquitto MQTT

```bash
sudo systemctl start mosquitto
```

# Test code in server side

publishされたデータをサーバ側でsubscribe。

```bash
mosquitto_sub -h www.kokis-website.org -p 8883 -t "home/temp" -u koki_tsuki -P Koki2501 --cafile /etc/mosquitto/certs/root_ca.crt
```
