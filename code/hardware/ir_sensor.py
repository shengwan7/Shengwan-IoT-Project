"""
hardware/ir_sensor.py - IR 避障感測器
"""

from machine import Pin
import config


class IrSensor:

    def __init__(self):
        self.pin = Pin(config.IR_PIN, Pin.IN)

    def detected(self):
        """回傳 True 表示偵測到物體。"""
        return self.pin.value() == config.IR_ACTIVE_LEVEL