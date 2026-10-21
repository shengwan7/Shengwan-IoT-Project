"""
web_server.py - ESP32 Lightweight Web Server (uasyncio 原生版)
"""

import uasyncio

try:
    import ujson as json
except ImportError:
    import json

import config
from hardware.rfid import new_rfid_state
from hardware.motion import new_motion_state
from hardware.led import LedBusyError
from communication.wifi import get_current_time

# ============================================================
# 全域變數
# ============================================================

mqtt_manager = None
publish_event = None
dht_sensor = None
rgb_led = None
light_sensor = None

wifi_ssid = None
wifi_password = None

rfid_state = new_rfid_state()
motion_state = new_motion_state()

light_history = []
LIGHT_HISTORY_MAX = 80
HTML_PAGE = None

# 新增：處理網頁點擊的綠閃任務
async def trigger_green_flash_from_web():
    if rgb_led is None or rgb_led.alert_active:
        return False
    
    rgb_led.alert_active = True
    rgb_led.save_state()
    date_str, weekday_str, time_str = get_current_time()
    rgb_led.add_flash_log(f"{date_str} {time_str}", "green")

    try:
        for _ in range(3):
            rgb_led.set_color_by_index(2) # 2 是綠色
            await uasyncio.sleep_ms(300)
            rgb_led.off()
            await uasyncio.sleep_ms(300)
    finally:
        rgb_led.restore_state()
        rgb_led.alert_active = False
        
    return True

# ============================================================
# 其他原本的函式
# ============================================================

def load_html():
    global HTML_PAGE
    try:
        with open('index.html', 'r') as f:
            HTML_PAGE = f.read()
        print("[Web] index.html 已載入,", len(HTML_PAGE), "bytes")
    except Exception as e:
        print("[Web] index.html 載入失敗:", e)
        HTML_PAGE = '<html><body><h1>Load Error</h1></body></html>'

def get_wifi_ip():
    try:
        import network
        wlan = network.WLAN(network.STA_IF)
        if wlan.isconnected():
            return wlan.ifconfig()[0]
    except Exception:
        pass
    return None

def get_current_temperature():
    try:
        if dht_sensor:
            return dht_sensor.temperature
    except Exception:
        pass
    return None

def get_current_humidity():
    try:
        if dht_sensor:
            return dht_sensor.humidity
    except Exception:
        pass
    return None

def get_current_light():
    global light_history
    try:
        if light_sensor:
            if hasattr(light_sensor, 'read'):
                value = light_sensor.read()
            elif hasattr(light_sensor, 'value'):
                value = light_sensor.value
            else:
                value = 0

            light_history.append(value)
            if len(light_history) > LIGHT_HISTORY_MAX:
                light_history.pop(0)
            return value
    except Exception:
        pass
    return 0

def get_sensor_json():
    temp = get_current_temperature()
    humidity = get_current_humidity()
    light = get_current_light()

    if temp is not None:
        temp = round(temp, 1)
    if humidity is not None:
        humidity = round(humidity, 1)

    led_info = {
        "alert_active": rgb_led.alert_active if rgb_led else False,
        "available": rgb_led is not None,
        "color_index": rgb_led.current_color_index if rgb_led else None,
        "is_on": rgb_led.is_on if rgb_led else False,
        "alert_flash_count": rgb_led.alert_flash_count if rgb_led else 0,
        "alert_flash_log": rgb_led.alert_flash_log if rgb_led else [],
        "alert_type": rgb_led.alert_type if rgb_led else None
    }

    return json.dumps({
        "temp": temp,
        "humidity": humidity,
        "light": light,
        "light_history": list(light_history),
        "status": "ok",
        "rfid": dict(rfid_state),
        "motion": dict(motion_state),
        "led": led_info,
    })

def http_header(status, content_type, content_length):
    return (
        'HTTP/1.1 ' + status + '\r\n'
        'Content-Type: ' + content_type + '\r\n'
        'Content-Length: ' + str(content_length) + '\r\n'
        'Connection: close\r\n'
        'Cache-Control: no-cache\r\n'
        'Access-Control-Allow-Origin: *\r\n'
        '\r\n'
    )

async def send_response(writer, body, content_type='text/html; charset=utf-8', status='200 OK'):
    try:
        body_bytes = body.encode('utf-8')
        header = http_header(status, content_type, len(body_bytes))
        writer.write(header.encode('utf-8'))
        chunk_size = 512
        for i in range(0, len(body_bytes), chunk_size):
            writer.write(body_bytes[i:i + chunk_size])
            await writer.drain()
        await writer.drain()
    except Exception as e:
        print("[Web] Response 傳送錯誤:", e)

def led_toggle():
    if rgb_led is None:
        return "unavailable"
    try:
        rgb_led.next_color()
        return "ok"
    except LedBusyError:
        return "busy"
    except Exception:
        return "error"

async def publish_once():
    if not wifi_ssid or not wifi_password:
        return False
    try:
        from communication.mqtt_client import MqttManager
        mgr = MqttManager(wifi_ssid, wifi_password)
        if not await mgr.connect():
            return False
        temp = get_current_temperature()
        humidity = get_current_humidity()
        msg = f'{config.DEVICE_NAME}：溫度：{temp}℃, 濕度：{humidity}%'
        await mgr.publish(config.MQTT_TOPICS['temp_humi'], msg, qos=0)
        await mgr.disconnect()
        return True
    except Exception:
        return False

async def handle_request(reader, writer):
    try:
        request_line = await reader.readline()
        if not request_line:
            return
        try:
            request_line = request_line.decode('utf-8').strip()
        except Exception:
            request_line = str(request_line)

        parts = request_line.split()
        if len(parts) < 2:
            await send_response(writer, '{"status":"error"}', 'application/json', '400 Bad Request')
            return

        method = parts[0]
        path = parts[1]

        while True:
            line = await reader.readline()
            if not line or line == b'\r\n' or line == b'\n':
                break

        if method == 'GET' and (path == '/' or path == '/index.html'):
            if HTML_PAGE is None:
                load_html()
            await send_response(writer, HTML_PAGE, 'text/html; charset=utf-8', '200 OK')

        elif method == 'GET' and path == '/favicon.ico':
            await send_response(writer, '', 'text/plain', '204 No Content')

        elif method == 'GET' and path == '/api/data':
            response = get_sensor_json()
            await send_response(writer, response, 'application/json; charset=utf-8', '200 OK')

        elif method == 'GET' and path == '/api/status':
            await send_response(writer, '{"status":"ok"}', 'application/json; charset=utf-8', '200 OK')

        elif method == 'POST' and path == '/api/led/toggle':
            result = led_toggle()
            if result == "ok":
                await send_response(writer, '{"status":"ok"}', 'application/json', '200 OK')
            elif result == "busy":
                await send_response(writer, '{"status":"busy"}', 'application/json', '409 Conflict')
            else:
                await send_response(writer, '{"status":"error"}', 'application/json', '500 Internal Server Error')

        # 處理網頁綠閃請求
        elif method == 'POST' and path == '/api/led/green_flash':
            success = await trigger_green_flash_from_web()
            if success:
                await send_response(writer, '{"status":"ok"}', 'application/json', '200 OK')
            else:
                await send_response(writer, '{"status":"busy"}', 'application/json', '409 Conflict')

        elif method == 'POST' and path == '/api/publish':
            ok = await publish_once()
            if ok:
                await send_response(writer, '{"status":"ok"}', 'application/json', '200 OK')
            else:
                await send_response(writer, '{"status":"error"}', 'application/json', '500 Internal Server Error')
        else:
            await send_response(writer, '{"status":"error","message":"Not Found"}', 'application/json', '404 Not Found')

    except Exception as e:
        print("[Web] Request 處理錯誤:", e)
        try:
            await send_response(writer, '{"status":"error"}', 'application/json', '500 Internal Server Error')
        except Exception:
            pass
    finally:
        try:
            writer.close()
        except Exception:
            pass

async def web_server_task():
    print("\n[Web] 初始化...")
    import gc
    gc.collect()
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.close()
    except Exception:
        pass

    load_html()
    wifi_ip = get_wifi_ip()
    if wifi_ip:
        print("[Web] 訪問: http://" + wifi_ip)

    try:
        await uasyncio.start_server(handle_request, '0.0.0.0', 80)
        print("[Web] ✅ Port 80 成功")
        while True:
            await uasyncio.sleep(3600)
    except Exception as e:
        print("[Web] ❌ Port 80 失敗:", e)
        try:
            await uasyncio.start_server(handle_request, '0.0.0.0', 8080)
            print("[Web] ✅ Port 8080 成功")
            if wifi_ip:
                print("[Web] 訪問: http://" + wifi_ip + ":8080")
            while True:
                await uasyncio.sleep(3600)
        except Exception as e2:
            print("[Web] ❌ 8080 也失敗:", e2)

async def sensor_monitor_task():
    while True:
        await uasyncio.sleep(10)

if __name__ == '__main__':
    print("[Web] web_server.py 已載入")