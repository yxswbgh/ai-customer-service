import json
import logging
import sys
from datetime import datetime,timezone
from typing import Any

class JSONFormatter(logging.Formatter):
    """将日志记录格式化为 JSON 行"""

    def format(self,record:logging.LogRecord)->str:
        log_entry:dict[str,Any]={
            "timestamp":datetime.fromtimestamp(
                record.created,
                tz=timezone.utc
            ).isoformat(),
            "level":record.levelname,
            "logger":record.name,
            "message":record.getMessage(),
            #filename 只有文件名（main.py），结合行号足够定位。
            "location":f"{record.filename}:{record.lineno}:{record.funcName}",
        }

        return json.dumps(log_entry,ensure_ascii=False) #中文日志直接输出中文，不需要 \uXXXX 转义。



def setup_logging(level:int=logging.INFO)->None:
    """配置根日志记录器，JSON 格式输出到 stdout"""
    root_logger=logging.getLogger()
    root_logger.setLevel(level)

    # 清除已有 handler，避免 reload 时重复
    root_logger.handlers.clear()

    handler=logging.StreamHandler(sys.stdout) # 创建 Handler：目标 = stdout（控制台）
    handler.setFormatter(JSONFormatter()) # 用刚刚定义的格式输出
    root_logger.addHandler(handler) #挂到root_logger上


def get_logger(name:str)->logging.Logger:
    """获取指定名称的日志记录器"""
    return logging.getLogger(name)

'''

Logger 是"产生日志的人"，Handler 是"送日志到哪去的人"

                    ┌─────────────┐
                    │   Logger    │  ← 写日志的人（"数据库连接超时！"）
                    │  (记录器)    │
                    └──────┬──────┘
                           │ 把日志消息递出去
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌─────────┐ ┌─────────┐ ┌─────────┐
        │Handler A│ │Handler B│ │Handler C│  ← 送信的人
        │ stdout  │ │ 文件    │ │ Slack   │
        └─────────┘ └─────────┘ └─────────┘
Logger 负责产生日志消息
Handler 负责把消息送达目的地（stdout、文件、网络、邮件……）
Logger 可以有多个 Handler，一条消息同时送到多个目的地


Logger 和 Handler 是分离的职责。 
Logger 只管"我要写日志"，不管写去哪。Handler 只管"把日志送到某处"，不管谁写的。
这个分离让你可以：
1.开发时只输出到 stdout
2.生产时同时输出到 stdout + 文件 + 告警
3.切换时只改配置，不改业务代码
'''
    
'''
Q: 为什么不用 logging.basicConfig()？

basicConfig() 只在第一次调用时生效，后续调用会被忽略。uvicorn 内部可能已经调用了它，所以手动配置 handler 更可靠。

Q: 生产环境想用 structlog 怎么办？

改 get_logger() 和 setup_logging() 两个函数即可，其他 50 个文件不用动。这就是封装的价值。
'''