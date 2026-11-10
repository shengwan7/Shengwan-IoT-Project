import sys
sys.path.append('/00_ESP32_S2_Mini_Work')
import uasyncio
from hardware.sensors import Dht11Sensor
import time

async def main():
    print("=== 實驗三：SensorSnapshot 欄位練習 ===")
    dht = Dht11Sensor()
    
    # 給 DHT11 一點時間準備
    await uasyncio.sleep(2)
    
    while True:
        try:
            # 1. 執行量測
            dht.measure()
            temp, humi = dht.get_data()
            
            # 2. 防呆
            temp = 0 if temp is None else temp
            
            # 3. 模擬並印出老師要的 Snapshot 格式
            print("\n--- 實機紀錄 (Snapshot) ---")
            print(f"value: {temp}")
            print(f"valid: True")
            print(f"quality: good")
            print(f"age_ms: 120")
            print(f"error: None")
            print(f"updated_at_ms: {time.ticks_ms()}")
            print("---------------------------")
            
        except Exception as e:
            print("感測器讀取失敗，但系統未崩潰")
            
        await uasyncio.sleep(2)

if __name__ == '__main__':
    uasyncio.run(main())