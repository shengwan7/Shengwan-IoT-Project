import sys
sys.path.append('/00_ESP32_S2_Mini_Work')
import uasyncio
import web_server

async def main():
    print("=== 實驗十：Web 狀態與非同步控制 ===")
    print("請開啟瀏覽器連線至 ESP32 IP")
    await web_server.web_server_task()

if __name__ == '__main__':
    uasyncio.run(main())