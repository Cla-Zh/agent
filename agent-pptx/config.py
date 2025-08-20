# config.py - 系统配置文件
import os
from typing import Dict, Any

class Config:
    """系统配置类"""
    
    # 服务器配置
    HOST = "0.0.0.0"
    PORT = 8000
    DEBUG = True
    
    # 并发配置
    MAX_CONCURRENT_SESSIONS = 100  # 最大并发会话数
    MAX_AGENTS_PER_SESSION = 6     # 每个会话的最大Agent数
    SESSION_TIMEOUT_HOURS = 24     # 会话超时时间（小时）
    CLEANUP_INTERVAL_SECONDS = 3600  # 清理任务间隔（秒）
    
    # Agent配置
    AGENT_THINKING_TIMEOUT = 300   # Agent思考超时时间（秒）
    AGENT_RETRY_COUNT = 3          # Agent重试次数
    
    # 内存管理
    MAX_MEMORY_USAGE_MB = 1024     # 最大内存使用量（MB）
    ENABLE_MEMORY_MONITORING = True
    
    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 安全配置
    ENABLE_RATE_LIMITING = True
    RATE_LIMIT_REQUESTS_PER_MINUTE = 60
    ENABLE_SESSION_VALIDATION = True
    
    # 性能配置
    ENABLE_CACHING = True
    CACHE_TTL_SECONDS = 300
    ENABLE_COMPRESSION = True
    
    # 监控配置
    ENABLE_METRICS = True
    METRICS_INTERVAL_SECONDS = 60
    
    @classmethod
    def get_concurrency_settings(cls) -> Dict[str, Any]:
        """获取并发相关设置"""
        return {
            "max_concurrent_sessions": cls.MAX_CONCURRENT_SESSIONS,
            "max_agents_per_session": cls.MAX_AGENTS_PER_SESSION,
            "session_timeout_hours": cls.SESSION_TIMEOUT_HOURS,
            "cleanup_interval_seconds": cls.CLEANUP_INTERVAL_SECONDS,
            "agent_thinking_timeout": cls.AGENT_THINKING_TIMEOUT,
            "agent_retry_count": cls.AGENT_RETRY_COUNT
        }
    
    @classmethod
    def get_performance_settings(cls) -> Dict[str, Any]:
        """获取性能相关设置"""
        return {
            "max_memory_usage_mb": cls.MAX_MEMORY_USAGE_MB,
            "enable_memory_monitoring": cls.ENABLE_MEMORY_MONITORING,
            "enable_caching": cls.ENABLE_CACHING,
            "cache_ttl_seconds": cls.CACHE_TTL_SECONDS,
            "enable_compression": cls.ENABLE_COMPRESSION
        }
    
    @classmethod
    def get_security_settings(cls) -> Dict[str, Any]:
        """获取安全相关设置"""
        return {
            "enable_rate_limiting": cls.ENABLE_RATE_LIMITING,
            "rate_limit_requests_per_minute": cls.RATE_LIMIT_REQUESTS_PER_MINUTE,
            "enable_session_validation": cls.ENABLE_SESSION_VALIDATION
        }

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    MAX_CONCURRENT_SESSIONS = 50
    SESSION_TIMEOUT_HOURS = 2

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = "WARNING"
    MAX_CONCURRENT_SESSIONS = 200
    SESSION_TIMEOUT_HOURS = 12
    ENABLE_RATE_LIMITING = True
    ENABLE_MEMORY_MONITORING = True

# 根据环境变量选择配置
def get_config():
    """根据环境变量获取配置"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionConfig
    else:
        return DevelopmentConfig

# 当前配置实例
current_config = get_config()