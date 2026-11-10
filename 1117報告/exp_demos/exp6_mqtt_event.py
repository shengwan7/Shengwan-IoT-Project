import sys
sys.path.append('/00_ESP32_S2_Mini_Work')
import uasyncio
from machine import Pin
import config

publish_event = uasyncio.Event()

async def button_task():
    btn = Pin(config.BUTTON1_PIN, Pin.IN, Pin.PULL_UP)
    while True:
        if btn.value() == 0:
            print("按鈕按下，設定 publish_event")
            publish_event.set()
            await uasyncio.sleep_ms(500)
        await uasyncio.sleep_ms(50)

async def mqtt_task():
    while True:
        await publish_event.wait()
        print("MQTT 任務收到 Event，準備發佈數據 (模擬)")
        publish_event.clear()
        await uasyncio.sleep(1)

async def main():
    print("=== 實驗六：MQTT 非同步發佈 ===")
    await uasyncio.gather(button_task(), mqtt_task())

if __name__ == '__main__':
    uasyncio.run(main())