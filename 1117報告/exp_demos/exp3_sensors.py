import sys
sys.path.append('/00_ESP32_S2_Mini_Work')
import uasyncio
from hardware.sensors import Dht11Sensor, LightSensor
from hardware.display import OledDisplay
import config

async def main():
    print("=== 實驗三：DHT11、光感與 OLED 的不同週期 ===")
    
    # 1. 初始化感測器與 OLED
    dht = Dht11Sensor()
    light = LightSensor()
    
    try:
        oled = OledDisplay()
        print("[Init] OLED 初始化成功")
    except Exception as e:
        print(f"[Init] OLED 初始化失敗: {e}")
        oled = None

    while True:
        try:
            # 2. 讀取實體感測器 (DHT11)
            dht.measure()
            temp, humi = dht.get_data()
            
            # 3. 防呆處理 (如果讀不到就給 0)
            temp = 0 if temp is None else temp
            humi = 0 if humi is None else humi
            
            # 4. 讀取光感
            light_val = light.read()
            
            # 5. OLED 只負責「顯示」，不負責「量測」
            if oled:
                line1 = f"溫度: {temp}C"
                line2 = f"濕度: {humi}%"
                oled.show_two_lines(line1, line2)
            
            # 6. 在終端機同步印出，方便觀察
            print(f"溫濕度: {temp}C {humi}% | 光感: {light_val}")
            
        except Exception as e:
            print(f"感測器讀取失敗，但系統未崩潰: {e}")
            
        # 非同步等待 2 秒，不卡死系統
        await uasyncio.sleep(2)

if __name__ == '__main__':
    uasyncio.run(main())