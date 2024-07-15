from datetime import datetime
import pytz
from tools.tool_base import toolbase

class Get_now(toolbase):
    

    def get_current_datetime(timezone, floor, building_number):
        print("我进来了。")
        tz = pytz.timezone(timezone)
        return datetime.now().astimezone(tz)
    # 自定义工具信息字典
    tool_info = {
        "tool_name": "get_now",
        "desc": "空调温度控制,比如说帮我调高一下温度，如果参数不全请继续提问。",
        "args": {
            "floor": (
                "int",
                "[*Required] 楼层"
            ),
            "building_number": (
                "int",
                "[*Required] 楼栋号"
            )
        },
        "func": get_current_datetime
    }
    # 向Agent实例注册自定义工具



