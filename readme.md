# 项目简介

这个项目使用 Agently 框架和本地部署的大模型来处理用户输入，根据模型的输出调用不同的工具，并返回结果给用户。该项目还包含一个 Flask 应用，用于处理前端和后端的交互。

## 文件结构

project/
├── main.py # 主程序入口，处理用户输入和调用其他模块
├── app.py # Flask 应用，处理前端和后端的交互
├── tools/
│ ├── weather_tool.py # 定义天气相关的工具功能
│ └── datetime_tool.py # 定义获取当前时间的工具功能
├── services/
│ ├── model.py # 包含与大模型交互的功能
│ └── history.py # 管理对话历史的存储和检索
├── config.py # 配置 Agently 代理
└── requirements.txt # 项目所需的所有依赖项


## 使用说明
1. 启动本地模型服务
假设您的本地模型已经启动并提供了 RESTful API 接口，您可以配置 config.py 文件以指向您的模型服务 URL。


2. 启动 Flask 应用
运行以下命令来启动 Flask 应用：
python app.py
Flask 应用将在 0.0.0.0:5000 上运行，并接受来自前端的请求。


3. API 端点
Flask 应用提供了一个 /chat 端点，您可以通过 POST 请求与之交互。请求格式如下：

请求格式：
{
    "user_id": "user123",
    "session_id": "session123",
    "message_id": "message123",
    "project_id": "project123",
    "ruler": "ruler123",
    "is_stream": false,
    "user_query": "北京的天气怎么样？"
}

响应格式：
{
    "user_id": "user123",
    "message_id": "message123",
    "create_time": 1672531199,
    "response_text": "北京的天气情况是...",
    "status":{
        "status_code": 200,
        "status_message": "agent各模块正常工作，成功返回答案。"
    }
}

