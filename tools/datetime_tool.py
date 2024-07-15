from datetime import datetime
import pytz
import Agently

def get_current_datetime(timezone):
    tz = pytz.timezone(timezone)
    return datetime.now().astimezone(tz)


tool_info = {
    "tool_name": "get_now",
    "desc": "获取当前时间",
    "args": {
        "timezone": (
            "str",
            "[*Required] 时区字符串，使用 pytz.timezone() 在 Python 中"
        )
    },
    "func": get_current_datetime
}

Agently.global_tool_manager.register(**tool_info)


