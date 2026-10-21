"""
hardware/buzzer.py - 蜂鳴器控制（含簡單旋律）
"""

from machine import Pin, PWM
import uasyncio
import config


class Buzzer:

    def __init__(self):
        self.pwm = PWM(Pin(config.BUZZER_PIN))
        self.pwm.duty(0)

    def _tone(self, freq):
        self.pwm.freq(freq)
        self.pwm.duty(config.BUZZER_DUTY)

    def off(self):
        self.pwm.duty(0)

    async def beep(self, freq=None, duration_ms=None):
        freq = freq or config.BUZZER_FREQUENCY
        duration_ms = duration_ms or config.BUZZER_DURATION_MS
        self._tone(freq)
        await uasyncio.sleep_ms(duration_ms)
        self.off()

    async def play_melody(self):
        """播放小蜜蜂前 4 個音。"""
        G4 = 392
        A4 = 440
        B4 = 494

        for n in [G4, G4, A4, B4]:
            self._tone(n)
            await uasyncio.sleep_ms(150)
            self.off()
            await uasyncio.sleep_ms(50)