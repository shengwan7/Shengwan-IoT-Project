"""
hardware/motion.py - PIR 移動偵測 + 音樂狀態容器
"""

def new_motion_state():
    return {
        "sensor_status": "starting",
        "detected": False,
        "direction": "unknown",
        "last_detected_at": None,
        "count": 0,
        "music_status": "unavailable",
        "sensor_error": None,
        "music_error": None,
        "history": [],
    }