import sys
sys.path.append('/00_ESP32_S2_Mini_Work')
import uasyncio
from machine import Pin
from hardware.led import RgbLed
import config

async def button1_task(rgb_led):
    btn = Pin(config.BUTTON1_PIN, Pin.IN, Pin.PULL_UP)
    while True:
        if btn.value() == 0:
            await uasyncio.sleep_ms(20)  # 去彈跳
            if btn.value() == 0:
                next_color = rgb_led.next_color()
                color_name = rgb_led.get_color_name(next_color)
                print(f"按鈕 1 按下：LED 切換為 {color_name}")
            while btn.value() == 0:
                await uasyncio.sleep_ms(10)
        await uasyncio.sleep_ms(10)

async def button2_task():
    btn = Pin(config.BUTTON2_PIN, Pin.IN, Pin.PULL_UP)
    while True:
        if btn.value() == 0:
            await uasyncio.sleep_ms(20)  # 去彈跳
            if btn.value() == 0:
                print("按鈕 2 按下：準備發佈 MQTT 數據...")
                try:
                    from communication.mqtt_client import MqttManager
                    mgr = MqttManager("124", "5201314aa") # 帶入你的 WiFi
                    if await mgr.connect():
                        msg = "實驗二：按鈕觸發 MQTT"
                        await mgr.publish(config.MQTT_TOPICS['temp_humi'], msg, qos=0)
                        await mgr.disconnect()
                        print("✅ MQTT 發佈成功！")
                    else:
                        print("❌ MQTT 連線失敗")
                except Exception as e:
                    print(f"❌ MQTT 異常: {e}")
                    
            while btn.value() == 0:
                await uasyncio.sleep_ms(10)
        await uasyncio.sleep_ms(10)

async def main():
    print("=== 實驗二：兩個按鈕與非同步去彈跳 ===")
    rgb_led = RgbLed()
    rgb_led.on(1) # 初始設為藍色
    
    await uasyncio.gather(
        button1_task(rgb_led),
        button2_task()
    )

if __name__ == '__main__':
    uasyncio.run(main())
