"""
hardware/rfid.py - RFID 狀態容器

目前先提供「狀態字典」，讓 Web API 能回傳前端要的欄位。
之後若接上 MFRC522，只要在 tasks.py 裡更新這份 state 即可。
"""


def new_rfid_state():
    """
    建立一份 RFID 狀態字典。

    欄位：
        last_uid       : 最後讀到的 UID（字串或 None）
        last_read_at   : 最後讀取時間（字串或 None）
        status         : starting / ready / init_error / read_error
        error          : 錯誤訊息（字串或 None）
    """
    return {
        "last_uid": None,
        "last_read_at": None,
        "status": "starting",
        "error": None,
    }