import sys
sys.path.append('/00_ESP32_S2_Mini_Work')
import uasyncio
from machine import Pin
import config
from hardware.buzzer import Buzzer

motion_event = uasyncio.Event()

async def pir_task():
    pir = Pin(config.IR_PIN, Pin.IN)
    while True:
        if pir.value() == 1:
            motion_event.set()
        await uasyncio.sleep_ms(100)

async def speaker_task():
    buzzer = Buzzer()
    while True:
        await motion_event.wait()
        print("偵測到移動！開始播放音樂 (真實發聲)")
        try:
            await buzzer.play_melody()
        except Exception as e:
            print(f"播放失敗: {e}")
        finally:
            buzzer.off()
        motion_event.clear()
        await uasyncio.sleep(1)

async def main():
    print("=== 實驗四：PIR Event 與喇叭 ===")
    await uasyncio.gather(pir_task(), speaker_task())

if __name__ == '__main__':
    uasyncio.run(main())