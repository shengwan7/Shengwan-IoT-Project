"""
hardware/rfid_reader.py - MFRC522 RFID 讀卡機封裝

使用 SoftSPI 版 mfrc522.py：
    MFRC522(sck, mosi, miso, rst, cs)
"""

import config
from mfrc522 import MFRC522


class RfidReader:

    def __init__(self):
        self.reader = MFRC522(
            sck=config.RFID_SCK_PIN,
            mosi=config.RFID_MOSI_PIN,
            miso=config.RFID_MISO_PIN,
            rst=config.RFID_RST_PIN,
            cs=config.RFID_CS_PIN,
        )

    def read_uid(self):
        """
        回傳 UID 字串（例如 'A1B2C3D4'），沒有卡片則回傳 None。
        """
        stat, _ = self.reader.request(self.reader.REQIDL)
        if stat != self.reader.OK:
            return None

        stat, raw_uid = self.reader.anticoll()
        if stat != self.reader.OK:
            return None

        # 舊版 anticoll 回傳 5 bytes（4 UID + 1 checksum）
        if len(raw_uid) < 4:
            return None

        uid = ''.join('{:02X}'.format(b) for b in raw_uid[:4])
        return uid