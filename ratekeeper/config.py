# ratekeeper/config.py
"""
ratekeeper 配置模块。

SHOWAPI_APPKEY 从环境中读取（支持 .env 文件 和 系统环境变量）。
"""

import os, sys
from dotenv import load_dotenv

def resource_path(rel_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, rel_path)
    return os.path.join(os.path.abspath("."), rel_path)

env_path = resource_path(".env")

# 加载项目根目录下的 .env 文件（如果存在）
load_dotenv(env_path, override=True)

# 从环境变量中读取 appKey
SHOWAPI_APPKEY: str | None = os.getenv("SHOWAPI_APPKEY")
# SHOWAPI_APPKEY: str | None = "078D1Ce9a4284fbB9ecB118F082f8cf2"

if not SHOWAPI_APPKEY:
    # 这里你可以选择：
    # 1. 直接 raise，让用户必须配置；或
    # 2. 打印警告，后面调用时再报错
    raise RuntimeError(
        "SHOWAPI_APPKEY is not set. "
        "Please create a .env file in project root with:\n"
        "SHOWAPI_APPKEY=your_real_key"
    )
