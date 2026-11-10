import sys
sys.path.append('/00_ESP32_S2_Mini_Work')
import uasyncio

async def fast_task():
    for i in range(5):
        print('fast', i)
        await uasyncio.sleep_ms(200)

async def slow_task():
    for i in range(3):
        print('slow', i)
        await uasyncio.sleep_ms(500)

async def main():
    print("=== 實驗一：兩個協程交錯執行 ===")
    await uasyncio.gather(fast_task(), slow_task())
    print("=== 實驗一結束 ===")

if __name__ == '__main__':
    uasyncio.run(main())