import Agently
agent = (
    Agently.create_agent()
        .set_settings("current_model", "OAIClient")
        .set_settings("model.OAIClient.auth.api_key", "nothing")  # 如果不需要 API key，可以为空
        .set_settings("model.OAIClient.options", {"model": "kagentlms_baichuan2_13b_mat"})  # 设置您的模型标识
        .set_settings("model.OAIClient.url", "http://localhost:8888/v1")  # 您本地模型的URL

)
"""定义并注册自定义工具"""
# 自定义工具函数及依赖
from datetime import datetime
import pytz
def get_current_datetime(timezone):
    tz = pytz.timezone(timezone)
    return datetime.now().astimezone(tz)
# 自定义工具信息字典
tool_info = {
    "tool_name": "get_now",
    "desc": "get current data and time",
    "args": {
        "timezone": (
            "str",
            "[*Required] Timezone string used in pytz.timezone() in Python"
        )
    },
    "func": get_current_datetime
}
# 向Agent实例注册自定义工具
agent.register_tool(
    tool_name = tool_info["tool_name"],
    desc = tool_info["desc"],
    args = tool_info["args"],
    func = tool_info["func"],
)
"""发起请求"""
print(agent.input("我在北京，现在几点了？").start())  