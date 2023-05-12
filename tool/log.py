import os
import sys
from .requests import post 
from loguru import logger

VER = "2.9"
log = logger
dir_log = "logs"
path_log = os.path.join(dir_log, '日志文件.log')
logger.remove()
logger.add(sys.stdout, level='INFO', colorize=True,
            format="<cyan>{module}</cyan>.<cyan>{function}</cyan>"
                    ":<cyan>{line}</cyan> - "+f"<cyan>{VER}</cyan> - "
                    "<level>{message}</level>"
            )
logger.add(path_log,
            format="{time:HH:mm:ss} - "
                    "{level}\t| "
                    "{module}.{function}:{line} - "+f"<cyan>{VER}</cyan> - "+" {message}",
            rotation='0:00', enqueue=True, serialize=False, encoding="utf-8", retention="10 days")

def webhook_and_log(message):
    log.info(message)
    from tool.config import read_json_file # Circular import
    url = read_json_file("config.json", False).get("webhook_url")
    if url == "" or url == None:
        return
    try:
        post(url, json={"content": message})
    except Exception as e:
        log.error(f"Webhook发送失败: {e}")
