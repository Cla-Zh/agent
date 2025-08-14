# config.py - 配置文件
import os
from typing import Optional

class Settings:
    """应用配置"""
    
    # 服务器配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Agent配置
    AGENT_THINKING_TIME_MIN: float = float(os.getenv("THINKING_TIME_MIN", "2.0"))
    AGENT_THINKING_TIME_MAX: float = float(os.getenv("THINKING_TIME_MAX", "8.0"))
    
    # 会话管理
    SESSION_EXPIRE_HOURS: int = int(os.getenv("SESSION_EXPIRE_HOURS", "24"))
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()