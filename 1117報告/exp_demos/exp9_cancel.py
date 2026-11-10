import sys
sys.path.append('/00_ESP32_S2_Mini_Work')
import uasyncio

async def worker():
    try:
        while True:
            print("任務執行中 (等待被取消)...")
            await uasyncio.sleep(1)
    finally:
        print("清理硬體：LED 已關閉 (安全狀態)")

async def main():
    print("=== 實驗九：任務取消與資源釋放 ===")
    task = uasyncio.create_task(worker())
    await uasyncio.sleep(2)
    print("準備取消任務...")
    task.cancel()
    await uasyncio.sleep(1) # 等待 finally 執行完

if __name__ == '__main__':
    uasyncio.run(main())