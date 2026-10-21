"""
main.py - 主程式進入點
ESP32 多感測器 IoT 系統
"""

import uasyncio
import gc
import config


async def initialize_system():

    print("\n" + "=" * 60)
    print("系統初始化")
    print("=" * 60 + "\n")

    print("[Init] 初始化基本硬體...")
    from hardware.led import RgbLed
    from hardware.button import Button
    from hardware.sensors import Dht11Sensor, LightSensor

    rgb_led = RgbLed()
    rgb_led.on(7)
    button1 = Button(config.BUTTON1_PIN)
    button2 = Button(config.BUTTON2_PIN)
    dht_sensor = Dht11Sensor()
    light_sensor = LightSensor()
    print("[Init] 基本硬體初始化完成")

    print("\n[Init] 初始化 RFID / IR / 蜂鳴器...")
    from hardware.rfid_reader import RfidReader
    from hardware.ir_sensor import IrSensor
    from hardware.buzzer import Buzzer

    rfid_reader = RfidReader()
    ir_sensor = IrSensor()
    buzzer = Buzzer()
    print("[Init] RFID / IR / 蜂鳴器初始化完成")

    gc.collect()
    print("[RAM] WiFi 前:", gc.mem_free())

    print("\n[Init] 初始化 WiFi...")
    from communication.wifi import connect_wifi
    ssid, password = await connect_wifi()
    print("[Init] WiFi 初始化完成")

    gc.collect()
    print("[RAM] WiFi 後:", gc.mem_free())

    print("\n[Init] 同步時間...")
    from communication.wifi import sync_time
    await sync_time()

    gc.collect()
    print("[RAM] 時間同步後:", gc.mem_free())

    from hardware.rfid import new_rfid_state
    from hardware.motion import new_motion_state

    rfid_state = new_rfid_state()
    motion_state = new_motion_state()

    print("\n[Init] 系統初始化完成\n")

    return (
        rgb_led, button1, button2,
        dht_sensor, light_sensor,
        ssid, password,
        rfid_state, motion_state,
        rfid_reader, ir_sensor, buzzer,
    )


async def main():

    (
        rgb_led, button1, button2,
        dht_sensor, light_sensor,
        ssid, password,
        rfid_state, motion_state,
        rfid_reader, ir_sensor, buzzer,
    ) = await initialize_system()

    publish_event = uasyncio.Event()

    print("[Main] 載入 tasks...")
    import tasks

    print("[Main] 載入 Web Server...")
    import web_server

    # 注入 web_server 全域物件
    web_server.publish_event = publish_event
    web_server.dht_sensor = dht_sensor
    web_server.rgb_led = rgb_led
    web_server.light_sensor = light_sensor
    web_server.rfid_state = rfid_state
    web_server.motion_state = motion_state

    # 注入 WiFi 帳密（給 /api/publish 按需連線用）
    web_server.wifi_ssid = ssid
    web_server.wifi_password = password

    gc.collect()
    print("[RAM] 所有模組載入後:", gc.mem_free())

    # ========================================================
    # 先啟動 Web Server
    # ========================================================

    print("\n[Main] 先啟動 Web Server...")
    ws_task = uasyncio.create_task(web_server.web_server_task())
    await uasyncio.sleep(2)

    gc.collect()
    print("[RAM] Web Server 啟動後:", gc.mem_free())

    # ========================================================
    # OLED
    # ========================================================

    print("\n[Main] 初始化 OLED...")
    try:
        from hardware.display import OledDisplay
        oled_display = OledDisplay()
        print("[Init] OLED 初始化成功")
    except Exception as e:
        print(f"[Init] OLED 初始化失敗: {e}")
        oled_display = None

    gc.collect()
    print("[RAM] OLED 後:", gc.mem_free())

    # ========================================================
    # DHT11 初測
    # ========================================================

    try:
        await uasyncio.sleep_ms(2000)
        dht_sensor.measure()
    except Exception as e:
        print(f"[DHT11] 初測失敗: {e}")

    # ========================================================
    # 啟動所有任務
    # ========================================================

    try:
        print("\n[Main] 啟動所有任務...\n")

        await uasyncio.gather(
            tasks.button1_task(button1, rgb_led, publish_event),
            tasks.button2_task_mqtt_ondemand(button2, dht_sensor, ssid, password),
            tasks.dht11_read_task(dht_sensor),
            tasks.light_sensor_task(light_sensor, rgb_led),
            tasks.oled_display_task(dht_sensor),
           tasks.rfid_task(rfid_state, rfid_reader),
            tasks.motion_task(motion_state, ir_sensor, buzzer),
            ws_task,
        )

    except KeyboardInterrupt:
        print("\n[Main] 程式被使用者中斷")
        rgb_led.off()

    except Exception as e:
        print(f"\n[Error] 主程式異常: {e}")
        try:
            rgb_led.off()
        except Exception:
            pass
        try:
            import traceback
            traceback.print_exc()
        except Exception:
            pass
