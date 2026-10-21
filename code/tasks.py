"""
tasks.py - 非同步任務協程
"""

import uasyncio
import time
import config
from hardware.led import RgbLed
from hardware.button import Button
from hardware.sensors import Dht11Sensor, LightSensor
from hardware.display import OledDisplay
from communication.wifi import get_current_time

# ==================== 任務：按鈕 1 ====================
async def button1_task(button1, rgb_led, publish_event):
    print("[Task] 按鈕 1 監聽已啟動")
    while True:
        try:
            await button1.wait_press()
            try:
                next_color = rgb_led.next_color()
                rgb_led.on(next_color)
                print(f"[LED] 按鈕1 切色: {rgb_led.get_color_name(next_color)}")
            except Exception as e:
                print(f"[LED] 無法切色: {e}")
            await button1.wait_release()
            await uasyncio.sleep_ms(100)
        except Exception:
            await uasyncio.sleep(1)


# ==================== 任務：按鈕 2 (MQTT) ====================
async def button2_task_mqtt_ondemand(button2, dht_sensor, ssid, password):
    print("[Task] 按鈕 2（MQTT）已啟動")
    while True:
        try:
            await button2.wait_press()
            try:
                from communication.mqtt_client import MqttManager
                mgr = MqttManager(ssid, password)
                if await mgr.connect():
                    temp, humi = dht_sensor.get_data()
                    msg = f'{config.DEVICE_NAME}：溫度：{temp}℃, 濕度：{humi}%'
                    await mgr.publish(config.MQTT_TOPICS['temp_humi'], msg, qos=0)
                    await mgr.disconnect()
                    print("[MQTT] 發布完成")
            except Exception as e:
                print(f"[MQTT] 異常: {e}")
            await button2.wait_release()
        except Exception:
            await uasyncio.sleep(1)


# ==================== 任務：按鈕 3 (綠閃) ====================
async def button3_task(button3, rgb_led):
    print("[Task] 按鈕 3（綠閃）監聽已啟動")
    while True:
        try:
            await button3.wait_press()
            
            # 如果正在警示中，直接忽略
            if rgb_led.alert_active:
                print("[Button3] 警示中，忽略綠閃")
                await button3.wait_release()
                continue
                
            print("[Button3] 觸發綠閃 3 次")
            rgb_led.alert_active = True
            rgb_led.save_state()  # 記住現在是什麼顏色
            
            date_str, weekday_str, time_str = get_current_time()
            rgb_led.add_flash_log(f"{date_str} {time_str}", "green")

            # 綠閃 3 次
            for _ in range(3):
                rgb_led.set_color_by_index(2) # 2 是綠色
                await uasyncio.sleep_ms(300)
                rgb_led.off()
                await uasyncio.sleep_ms(300)
                
            rgb_led.restore_state() # 恢復原本顏色
            rgb_led.alert_active = False
            print("[Button3] 綠閃結束，已恢復原色")
            
            await button3.wait_release()
        except Exception:
            await uasyncio.sleep(1)


# ==================== 任務：DHT11 ====================
async def dht11_read_task(dht_sensor):
    while True:
        try:
            dht_sensor.measure()
            await uasyncio.sleep(config.DHT11_POLL_INTERVAL_SEC)
        except Exception:
            await uasyncio.sleep(config.DHT11_POLL_INTERVAL_SEC)


# ==================== 任務：光感測器（紅閃） ====================
async def light_sensor_task(light_sensor, rgb_led):
    print("[Task] 光感測器任務已啟動")
    triggered = False

    while True:
        try:
            brightness = light_sensor.read()

            if brightness < config.LIGHT_THRESHOLD_ON:
                if not triggered and not rgb_led.alert_active:
                    triggered = True
                    print(f"[Light] 太暗！開始紅閃 5 次")
                    
                    rgb_led.alert_active = True
                    rgb_led.save_state()
                    
                    date_str, weekday_str, time_str = get_current_time()
                    rgb_led.add_flash_log(f"{date_str} {time_str}", "red")

                    for _ in range(5):
                        rgb_led.set_color_by_index(4) # 4 是紅色
                        await uasyncio.sleep_ms(100)
                        rgb_led.off()
                        await uasyncio.sleep_ms(100)
                    
                    rgb_led.restore_state()
                    rgb_led.alert_active = False
                    print(f"[Light] 紅閃結束，已恢復原色")

            elif brightness > config.LIGHT_THRESHOLD_OFF:
                triggered = False

            await uasyncio.sleep_ms(config.LIGHT_POLL_INTERVAL_MS)

        except Exception as e:
            await uasyncio.sleep_ms(config.LIGHT_POLL_INTERVAL_MS)


# ==================== 任務：OLED ====================
async def oled_display_task(dht_sensor):
    oled = None
    try:
        oled = OledDisplay()
    except Exception:
        pass
    while True:
        try:
            date_str, weekday_str, time_str = get_current_time()
            temp, humi = dht_sensor.get_data()
            if oled:
                oled.show_two_lines(f"{date_str} {time_str[:5]}", f"{temp}C {humi}%")
            await uasyncio.sleep(1)
        except Exception:
            await uasyncio.sleep(1)


# ==================== 任務：RFID ====================
async def rfid_task(rfid_state, rfid_reader):
    last_uid = None
    while True:
        try:
            uid = rfid_reader.read_uid()
            if uid and uid != last_uid:
                rfid_state["last_uid"] = uid
                rfid_state["last_read_at"] = get_current_time()[2]
                last_uid = uid
            elif not uid:
                last_uid = None
            await uasyncio.sleep_ms(config.RFID_POLL_INTERVAL_MS)
        except Exception:
            await uasyncio.sleep(1)


# ==================== 任務：PIR ====================
async def motion_task(motion_state, ir_sensor, buzzer):
    was_detected = False
    is_inside = False
    while True:
        try:
            now = ir_sensor.detected()
            if now and not was_detected:
                is_inside = not is_inside
                action = "進來" if is_inside else "出去"
                time_str = get_current_time()[2]
                motion_state["count"] += 1
                motion_state["history"].append({"time": time_str, "action": action, "count": motion_state["count"]})
                if len(motion_state["history"]) > 5:
                    motion_state["history"].pop(0)
                await buzzer.play_melody()
            was_detected = now
            await uasyncio.sleep_ms(config.IR_POLL_INTERVAL_MS)
        except Exception:
            await uasyncio.sleep(1)