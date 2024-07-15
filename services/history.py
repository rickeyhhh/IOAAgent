import redis
import json
import time
import logging
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.logging_config import *
from entities import ChatRequest  # 导入实体类

# 初始化 Redis 客户端
r = redis.Redis(host='localhost', port=6379, db=0)

def store_history(chat_request, model_output):  # 存历史记录
    try:
        timestamp = int(time.time())
        history_record = {
            'user_input': chat_request.user_query,
            'model_output': model_output,
            'timestamp': timestamp
        }
        r.rpush(f"history:{chat_request.user_id}:{chat_request.session_id}", json.dumps(history_record))
        logging.debug(f"存储用户： {chat_request.user_id} 在对话： {chat_request.session_id}: {history_record}")
    except Exception as e:
        logging.error(f"存储用户： {chat_request.user_id} 在对话：{chat_request.session_id}中的聊天记录出现错误: {e}", exc_info=True)

def get_history(chat_request: ChatRequest):  # 读历史记录
    try:
        history = r.lrange(f"history:{chat_request.user_id}:{chat_request.session_id}", 0, -1)
        history_records = [json.loads(record) for record in history]
        logging.debug(f"读取用户： {chat_request.user_id} 在对话：{chat_request.session_id}中的聊天记录: {history_records}")
        return history_records
    except Exception as e:
        logging.error(f"读取用户： {chat_request.user_id} 在对话： {chat_request.session_id}中的聊天记录出现错误: {e}", exc_info=True)
        return []
