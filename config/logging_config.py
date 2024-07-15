import logging
from logging.handlers import TimedRotatingFileHandler
import os
from datetime import datetime

log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')

# 设置日志文件路径和名称，包含当前日期
current_date = datetime.now().strftime('%Y-%m-%d')
log_file = os.path.join(log_dir, f'application_{current_date}.log')

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')

# 时间轮转文件, 每天生成一个文件，同时保留七个文件。
file_handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1, backupCount=7)
file_handler.suffix = '%Y-%m-%d.log'
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logging.getLogger().addHandler(file_handler)
