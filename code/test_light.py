"""	est_light.py - 獨立作業：太暗閃 5 次 + 變色 + 按鈕 1 切色

硬體：
- 光敏電阻模組（LDR）→ GPIO34
- RGB LED → GPIO25 / 26 / 33
- 按鈕 1 → GPIO16

功能：
1. 太暗（光敏值 < LIGHT_THRESHOLD_ON，連續 N 次確認）：
   - 紅燈閃 5 次
   - 閃完後切換到下一個顏色
2. 按鈕 1：
   - 正常時：切換到下一個顏色
   - 警示閃爍中：無效

執行：
    >>> import test_light
    >>> import uasyncio
    >>> uasyncio.run(test_light.main())
"""

import uasyncio
from machine import Pin, ADC
from hardware.led import RgbLed, LedBusyError
from hardware.button import Button


# ==================== 參數（獨立作業，直接寫在這裡）====================

# 光線門檻（依實際讀值調整）
LIGHT_THRESHOLD_ON = 1500     # 低於此值 → 太暗
LIGHT_THRESHOLD_OFF = 1800    # 高於此值 → 太亮

# 連續確認次數
DARK_CONFIRM_COUNT = 2
BRIGHT_CONFIRM_COUNT = 2

# 光感測器腳位
LIGHT