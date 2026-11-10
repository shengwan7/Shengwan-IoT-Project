import sys
sys.path.append('/00_ESP32_S2_Mini_Work')
import uasyncio
from hardware.rfid_reader import RfidReader

async def main():
    print("=== 實驗七：RFID 非同步讀取 ===")
    reader = RfidReader()
    while True:
        try:
            uid = reader.read_uid()
            if uid:
                print(f"讀到卡號: {uid}")
        except Exception as e:
            print("RFID 通訊錯誤，系統未崩潰")
        await uasyncio.sleep_ms(500)

if __name__ == '__main__':
    uasyncio.run(main())