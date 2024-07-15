import requests
import Agently

def get_weather(city):
    print(city + "我进到了getweather这个函数了！")
    url = f"https://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city={city}&needMoreData=true&pageNo=1&pageSize=7"
    response = requests.get(url)
    return response.json() + '我进到了getweather这个函数了！'


Agently.global_tool_manager.register(
    tool_name="weather",
    desc="获取天气信息",
    args={
        "city": ("String", "[*Required] 获取天气所需要的城市名称")
    },
    func=get_weather
)


