"""
config.py - 全域配置文件
"""

# ==================== RGB LED ====================
LED_RED_PIN = 25
LED_GREEN_PIN = 26
LED_BLUE_PIN = 33

# ==================== 按鈕 ====================
BUTTON1_PIN = 16
BUTTON2_PIN = 17

# ==================== DHT11 ====================
DHT11_PIN = 27

# ==================== 光感測器 ====================
TEMT_ADC_PIN = 34

# ==================== OLED ====================
I2C_ID = 0
I2C_SCL_PIN = 22
I2C_SDA_PIN = 21
OLED_WIDTH = 128
OLED_HEIGHT = 64

# ==================== RFID ====================
RFID_SCK_PIN = 18
RFID_MOSI_PIN = 23
RFID_MISO_PIN = 19
RFID_RST_PIN = 4
RFID_CS_PIN = 5

# ==================== 蜂鳴器 ====================
BUZZER_PIN = 14

# ==================== 紅外線感測器 ====================
IR_PIN = 13

# ==================== 光感測器參數 ====================
LIGHT_THRESHOLD_ON = 600
LIGHT_THRESHOLD_OFF = 2000
LIGHT_POLL_INTERVAL_MS = 50

# ==================== DHT11 ====================
DHT11_POLL_INTERVAL_SEC = 2

# ==================== OLED ====================
OLED_UPDATE_INTERVAL_SEC = 1

# ==================== RFID ====================
RFID_POLL_INTERVAL_MS = 500

# ==================== 按鈕 ====================
BUTTON_DEBOUNCE_MS = 20
BUTTON_POLL_INTERVAL_MS = 30

# ==================== 蜂鳴器 ====================
BUZZER_FREQUENCY = 2000
BUZZER_DUTY = 512
BUZZER_DURATION_MS = 100

# ==================== 紅外線感測器 ====================
IR_POLL_INTERVAL_MS = 50
IR_ACTIVE_LEVEL = 1

# ==================== WiFi ====================
WIFI_PROFILES = {
    '124': '5201314aa',
}

TIMEZONE_OFFSET_SEC = 8 * 3600

# ==================== MQTT ====================
MQTT_BROKER = 'broker.emqx.io'
MQTT_PORT = 1883

MQTT_TOPICS = {
    'cmd': b'nuu/csie/milkyfrog/cmd01',
    'temp_humi': b'nuu/csie/milkyfrog/TempHumi',
    'subscribe': b'nuu/csie/milkyfrog/#',
}

MQTT_RECONNECT_INITIAL_DELAY_SEC = 2
MQTT_RECONNECT_MAX_DELAY_SEC = 60
MQTT_RECONNECT_BACKOFF_FACTOR = 1.5

# ==================== 字體 ====================
FONT_PATH = './lib/fonts/fusion_bdf.12'

# ==================== RGB LED 顏色對應 ====================
COLOR_MAP = {
    0: ('黑', 0b000),
    1: ('藍', 0b001),
    2: ('綠', 0b010),
    3: ('青', 0b011),
    4: ('紅', 0b100),
    5: ('紫', 0b101),
    6: ('黃', 0b110),
    7: ('白', 0b111),
}

# ==================== 裝置識別 ====================
DEVICE_NAME = '奶蛙的IoT裝置'
DEVICE_ID = 'milkyfrog'