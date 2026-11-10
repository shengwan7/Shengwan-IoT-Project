import sys
sys.path.append('/00_ESP32_S2_Mini_Work')
import uasyncio

async def fake_network():
    print("嘗試連線中... (預計要 3 秒)")
    await uasyncio.sleep(3)
    return "連線成功"

async def main():
    print("=== 實驗八：Timeout 與安全清理 ===")
    try:
        await uasyncio.wait_for(fake_network(), timeout=1)
        print("成功收到回應")
    except uasyncio.TimeoutError:
        print("錯誤：連線逾時 (Timeout)，系統安全退出")

if __name__ == '__main__':
    uasyncio.run(main())