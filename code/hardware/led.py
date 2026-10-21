"""
hardware/led.py - RGB LED 控制模組
"""

from machine import Pin
import config


class LedBusyError(Exception):
    """LED 正在警示中，暫時不接受切色指令。"""
    pass


class RgbLed:

    def __init__(self):
        self.red = Pin(config.LED_RED_PIN, Pin.OUT)
        self.green = Pin(config.LED_GREEN_PIN, Pin.OUT)
        self.blue = Pin(config.LED_BLUE_PIN, Pin.OUT)

        self.current_color_index = 0
        self.is_on = False
        self.alert_active = False
        
        # 紀錄警示狀態與次數
        self.alert_type = None    # 'red' 或 'green' 或 None
        self.alert_flash_count = 0
        self.alert_flash_log = []
        
        # 紀錄閃爍前原本的顏色與開關狀態
        self.saved_color = 0
        self.saved_is_on = False

        self.off()

    def set_color_by_index(self, index):
        index = index % 8
        self.current_color_index = index

        r = (index >> 2) & 1
        g = (index >> 1) & 1
        b = index & 1

        self.red.value(r)
        self.green.value(g)
        self.blue.value(b)

        self.is_on = (index != 0)

    def get_color_name(self, index):
        return config.COLOR_MAP.get(index % 8, ('未知', 0b000))[0]

    def on(self, index=None):
        if index is not None:
            self.current_color_index = (index % 8)
        index = self.current_color_index
        r = (index >> 2) & 1
        g = (index >> 1) & 1
        b = index & 1
        self.red.value(r)
        self.green.value(g)
        self.blue.value(b)
        self.is_on = (index != 0)

    def off(self):
        self.red.value(0)
        self.green.value(0)
        self.blue.value(0)
        self.is_on = False

    def next_color(self):
        if self.alert_active:
            raise LedBusyError("警示中，暫停切色")
        next_index = (self.current_color_index + 1) % 8
        self.set_color_by_index(next_index)
        return next_index

    def toggle(self):
        if self.is_on:
            self.off()
        else:
            self.on()

    # 加入閃爍紀錄
    def add_flash_log(self, time_str, alert_type):
        self.alert_type = alert_type
        self.alert_flash_count += 1
        self.alert_flash_log.append({
            "sequence": self.alert_flash_count,
            "time": time_str,
            "type": alert_type
        })
        if len(self.alert_flash_log) > 5:
            self.alert_flash_log.pop(0)
            
    # 儲存當前狀態
    def save_state(self):
        self.saved_color = self.current_color_index
        self.saved_is_on = self.is_on
        
    # 恢復儲存的狀態
    def restore_state(self):
        if self.saved_is_on:
            self.on(self.saved_color)
        else:
            self.off()