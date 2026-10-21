"""
communication/wifi.py - WiFi 連線管理

功能：
- 使用 config.py 的 WIFI_PROFILES
- 直接連線，不進行 WiFi 掃描
- 同步系統時間
- 取得目前時間
"""

import network
import time
import config


# ============================================================
# WiFi 連線
# ============================================================

async def connect_wifi():
    """
    使用 config.WIFI_PROFILES 直接連線 WiFi。

    不使用 ns_tools.connect_to_known_wifi()
    避免 WiFi 掃描造成記憶體不足。

    返回：
        (ssid, password)
    """

    print("[WiFi] 嘗試連線到 WiFi...")

    wlan = network.WLAN(network.STA_IF)

    # 啟用 Station 模式
    wlan.active(True)

    # 如果已經連線
    if wlan.isconnected():

        ssid = wlan.config('essid')

        print(f"[WiFi] 已經連線到: {ssid}")
        print(f"[WiFi] IP: {wlan.ifconfig()[0]}")

        # 找出對應的密碼
        password = config.WIFI_PROFILES.get(
            ssid,
            ""
        )

        return ssid, password

    # 逐一嘗試 config.py 中的 WiFi
    for ssid, password in config.WIFI_PROFILES.items():

        print(f"[WiFi] 嘗試連線: {ssid}")

        try:
            wlan.disconnect()
        except Exception:
            pass

        try:
            wlan.connect(ssid, password)

            # 最多等待 15 秒
            for _ in range(30):

                if wlan.isconnected():
                    break

                await_sleep_ms(500)

            if wlan.isconnected():

                print(
                    f"[WiFi] WiFi 連線成功: {ssid}"
                )

                print(
                    f"[WiFi] IP: "
                    f"{wlan.ifconfig()[0]}"
                )

                return ssid, password

            print(
                f"[WiFi] 連線失敗: {ssid}"
            )

        except Exception as e:

            print(
                f"[WiFi] 連線錯誤: {e}"
            )

    print("[WiFi] 所有 WiFi 連線都失敗")

    # 保留原本程式需要的回傳格式
    ssid = list(
        config.WIFI_PROFILES.keys()
    )[0]

    password = config.WIFI_PROFILES[ssid]

    return ssid, password


# ============================================================
# 非同步 sleep
# ============================================================

async def _async_sleep_ms(ms):
    import uasyncio
    await uasyncio.sleep_ms(ms)


def await_sleep_ms(ms):
    """
    這個函式只是為了避免在某些 MicroPython
    版本中直接使用 asyncio.sleep_ms 時造成問題。

    connect_wifi() 會透過簡單的事件循環等待。
    """

    time.sleep_ms(ms)


# ============================================================
# 時間同步
# ============================================================

async def sync_time():
    """
    同步系統時間。

    優先使用：
        ns_tools.mySetTime()

    失敗後嘗試：
        aiot_tools.set_time()

    時區使用：
        config.TIMEZONE_OFFSET_SEC
    """

    print("[Time] 同步系統時間...")

    timezone_hours = (
        config.TIMEZONE_OFFSET_SEC // 3600
    )

    # --------------------------------------------------------
    # 嘗試 ns_tools
    # --------------------------------------------------------

    try:

        from ns_tools import mySetTime

        result = mySetTime(
            timezone=timezone_hours,
            max_retries=3
        )

        if result:

            print(
                "[Time] 時間已同步 (ns_tools)"
            )

            return True

    except Exception as e:

        print(
            f"[Time] ns_tools 時間同步失敗: {e}"
        )

    # --------------------------------------------------------
    # 嘗試 aiot_tools
    # --------------------------------------------------------

    try:

        from aiot_tools import set_time

        set_time(
            timezone=timezone_hours
        )

        print(
            "[Time] 時間已同步 (aiot_tools)"
        )

        return True

    except Exception as e:

        print(
            f"[Time] aiot_tools 時間同步失敗: {e}"
        )

    print(
        "[Time] 時間同步失敗，"
        "使用系統預設時間"
    )

    return False


# ============================================================
# 取得目前時間
# ============================================================

def get_current_time():
    """
    取得格式化的本地時間。

    返回：
        (
            date_str,
            weekday_str,
            time_str
        )
    """

    # --------------------------------------------------------
    # 優先使用 ns_tools
    # --------------------------------------------------------

    try:

        from ns_tools import myGetTime

        return myGetTime()

    except ImportError:

        pass

    except Exception as e:

        print(
            f"[Time] ns_tools 取得時間失敗: {e}"
        )

    # --------------------------------------------------------
    # 嘗試 aiot_tools
    # --------------------------------------------------------

    try:

        from aiot_tools import get_time

        return get_time()

    except ImportError:

        pass

    except Exception as e:

        print(
            f"[Time] aiot_tools 取得時間失敗: {e}"
        )

    # --------------------------------------------------------
    # 使用系統時間
    # --------------------------------------------------------

    now = time.localtime()

    weekdays = [
        "一",
        "二",
        "三",
        "四",
        "五",
        "六",
        "日"
    ]

    date_str = "{:04d}/{:02d}/{:02d}".format(
        now[0],
        now[1],
        now[2]
    )

    time_str = "{:02d}:{:02d}:{:02d}".format(
        now[3],
        now[4],
        now[5]
    )

    weekday_str = weekdays[now[6]]

    return (
        date_str,
        weekday_str,
        time_str
    )

