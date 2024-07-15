from datetime import datetime
import Agently
import pytz
import json

instruction_data = {
            "property": "WD",
            "propertyName": "温度",
            "valueType": "double",
            "value": 27.5,
            "updateTime": "2024-05-28 16:49:51",
            "description": "该点位代表当前温度，温度的测量范围为：16度到45度之间",
}

def query_device_info(device_id):
    instruction_data = {
            "property": "WD",
            "propertyName": "温度",
            "valueType": "double",
            "value": 27.5,
            "updateTime": "2024-05-28 16:49:51",
            "description": "该点位代表当前温度，温度的测量范围为：16度到45度之间",
        }
    if device_id == "12345":
        return(instruction_data)

tool_info = {
    "tool_name": "query_device_info",
    "desc": "Use device id to query device info.",
    "args": {
        "device_id": (
            "json",
            "[*Required] Device_id"
        )
    },
    "func": query_device_info
}

Agently.global_tool_manager.register(**tool_info)