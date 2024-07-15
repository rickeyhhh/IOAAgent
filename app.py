# app.py
from flask import Flask, request, jsonify
from datetime import datetime
import logging
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

# 导入日志配置
from config.logging_config import *
from main import process_input
from entities import ChatRequest  # 导入实体类

app = Flask(__name__)


def validate_request(data):
    required_fields = ['user_id', 'session_id', 'message_id', 'user_query']
    for field in required_fields:
        if field not in data:
            return False, f"缺少必填参数: {field}"
    return True, None

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        logging.debug(f"接收到请求数据： {data}")

        is_valid, error_message = validate_request(data)  # 验证请求数据
        if not is_valid:
            logging.warning(f"验证错误: {error_message}")
            return jsonify({
                "status": {
                    "status_code": 400,
                    "status_message": error_message
                }
            }), 400

        # 创建 ChatRequest 实例
        chat_request = ChatRequest(
            user_id=data.get('user_id'),
            session_id=data.get('session_id'),
            message_id=data.get('message_id'),
            project_id=data.get('project_id'),
            ruler_list=data.get('ruler', {}).get('items', []),
            is_stream=data.get('is_stream', False),
            user_query=data.get('user_query')
        )

        logging.debug(f"创建ChatRequest实体: {chat_request}")

        response_text = process_input(chat_request)  # 调用主处理函数

        create_time = int(datetime.now().timestamp())

        response = {
            "user_id": chat_request.user_id,
            "message_id": chat_request.message_id,
            "create_time": create_time,
            "response_text": response_text,
            "status": {
                "status_code": 200,
                "status_message": "agent各模块正常工作，成功返回答案。"
            }
        }

        logging.debug(f"Response: {response}")
        return jsonify(response)

    except Exception as e:
        logging.error(f"Error occurred: {e}", exc_info=True)
        return jsonify({
            "status": {
                "status_code": 500,
                "status_message": "网络服务错误。"
            }
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
