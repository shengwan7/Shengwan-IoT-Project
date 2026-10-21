"""
communication/mqtt_client.py - 輕量 MQTT 客戶端管理

使用 umqtt.simple，只佔極少記憶體。
"""

import uasyncio
import config
import sys

LIB_PATH = "/00_ESP32_S2_Mini_Work/lib"
if LIB_PATH not in sys.path:
    sys.path.append(LIB_PATH)

from umqtt.simple import MQTTClient


class MqttManager:

    def __init__(self, ssid, password, broker=None):
        self.ssid = ssid
        self.password = password
        self.broker = broker or config.MQTT_BROKER
        self.client = MQTTClient(
            client_id="esp32_" + config.DEVICE_ID,
            server=self.broker,
            port=config.MQTT_PORT,
            keepalive=60,
        )
        self._connected = False
        print("[MQTT] 已初始化（umqtt.simple）")
        print(f"[MQTT] Broker: {self.broker}:{config.MQTT_PORT}")

    async def connect(self):
        try:
            print(f"[MQTT] 嘗試連線到 {self.broker}...")
            self.client.connect()
            self._connected = True
            print("[MQTT] 已連線成功")
            return True
        except Exception as e:
            print(f"[MQTT] 連線失敗: {e}")
            self._connected = False
            return False

    async def wait_connected(self, timeout_sec=30):
        return self._connected

    async def publish(self, topic, message, qos=0):
        try:
            if isinstance(topic, str):
                topic = topic.encode()
            if isinstance(message, str):
                message = message.encode()
            self.client.publish(topic, message)
            print(f"[MQTT] 已發佈: {topic}")
            return True
        except Exception as e:
            print(f"[MQTT] 發佈失敗: {e}")
            return False

    async def subscribe(self, topic, qos=0, callback=None):
        try:
            if callback:
                def cb(t, m):
                    try:
                        uasyncio.create_task(callback(m))
                    except Exception:
                        pass
                self.client.set_callback(cb)
            if isinstance(topic, str):
                topic = topic.encode()
            self.client.subscribe(topic, qos=qos)
            print(f"[MQTT] 已訂閱: {topic}")
            return True
        except Exception as e:
            print(f"[MQTT] 訂閱失敗: {e}")
            return False

    async def disconnect(self):
        try:
            self.client.disconnect()
            self._connected = False
            print("[MQTT] 已斷線")
        except Exception as e:
            print(f"[MQTT] 斷線失敗: {e}")

    def is_connected(self):
        return self._connected