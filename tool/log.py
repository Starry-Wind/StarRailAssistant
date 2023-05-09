import os
import sys
from loguru import logger

log = logger
dir_log = "logs"
path_log = os.path.join(dir_log, '日志文件.log')
logger.remove()
logger.add(sys.stdout, level='INFO', colorize=True,
            format="<cyan>{module}</cyan>.<cyan>{function}</cyan>"
                    ":<cyan>{line}</cyan> - "
                    "<level>{message}</level>"
            )
logger.add(path_log,
            format='{time:HH:mm:ss} - '  # 时间
                    '{level}\t| '
                    '{module}.{function}:{line} - {message}',
            rotation='0:00', enqueue=True, serialize=False, encoding="utf-8", retention="10 days")