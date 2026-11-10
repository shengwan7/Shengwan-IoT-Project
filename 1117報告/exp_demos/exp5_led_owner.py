import sys
sys.path.append('/00_ESP32_S2_Mini_Work')
import uasyncio
from hardware.led import RgbLed, LedBusyError

async def main():
    print("=== 實驗五：RGB LED 單一 owner 控制 ===")
    led = RgbLed()
    
    # 1. 先指定亮紅色，讓老師看清楚
    led.on(4) # 4 是紅色
    print("初始狀態：紅色 (索引 4)")
    await uasyncio.sleep(1) # 停一秒讓你觀察
    
    # 2. 嘗試正常切色 (會變成下一個顏色)
    print("嘗試正常切色...")
    led.next_color()
    print("切色成功")
    await uasyncio.sleep(1)
    
    # 3. 模擬警示狀態
    print("模擬進入警示狀態 (alert_active = True)")
    led.alert_active = True
    
    # 4. 警示中嘗試切色
    print("警示中嘗試切色...")
    try:
        led.next_color()
    except LedBusyError:
        print("錯誤：警示中，拒絕切色 (LedBusyError)")
        
    led.alert_active = False
    print("警示解除，恢復正常")

if __name__ == '__main__':
    uasyncio.run(main())