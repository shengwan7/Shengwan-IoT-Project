"""
hardware/display.py - OLED 顯示模組
"""

import sys

# ============================================================
# 加入 lib 資料夾
# ssd1306.py 位於：
# /00_ESP32_S2_Mini_Work/lib/
# ============================================================

LIB_PATH = "/00_ESP32_S2_Mini_Work/lib"

if LIB_PATH not in sys.path:
    sys.path.append(LIB_PATH)


from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import config


# ============================================================
# 中文字型
# ============================================================

try:
    from bitmap_font_tool import set_font_path, draw_text

    _HAS_FONT = True

    set_font_path(config.FONT_PATH)

except Exception:

    _HAS_FONT = False
    draw_text = None


# ============================================================
# OLED 顯示類別
# ============================================================

class OledDisplay:

    def __init__(self):

        # ----------------------------------------------------
        # 初始化 I2C
        # ----------------------------------------------------

        self._i2c = I2C(
            config.I2C_ID,
            scl=Pin(config.I2C_SCL_PIN),
            sda=Pin(config.I2C_SDA_PIN)
        )

        # ----------------------------------------------------
        # 初始化 OLED
        # ---------------------------------------------------

        self._oled = SSD1306_I2C(
            config.OLED_WIDTH,
            config.OLED_HEIGHT,
            self._i2c
        )

        self._has_font = _HAS_FONT

        self._draw_text = (
            draw_text
            if _HAS_FONT
            else None
        )

        print(
            "[OLED] OledDisplay 初始化完成 "
            f"(SCL={config.I2C_SCL_PIN}, "
            f"SDA={config.I2C_SDA_PIN}, "
            f"{config.OLED_WIDTH}x{config.OLED_HEIGHT})"
        )


    # ======================================================