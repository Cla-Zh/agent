# monitoring.py - 监控和性能管理模块
import asyncio
import time
import threading
from typing import Dict, List, Any
from datetime import datetime, timedelta
import logging
from collections import defaultdict, deque
import json

from config import current_config

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {
            "active_sessions": deque(maxlen=100),
            "request_count": deque(maxlen=100),
            "response_times": deque(maxlen=100),
            "error_count": deque(maxlen=100)
        }
        self.session_stats = defaultdict(lambda: {
            "created_at": None,
            "last_accessed": None,
            "request_count": 0,
            "total_response_time": 0,
            "error_count": 0
        })
        self._lock = threading.RLock()
        self._monitoring_task = None
        self._start_time = time.time()
    
    def start_monitoring(self):
        """启动监控"""
        if self._monitoring_task is None:
            self._monitoring_task = asyncio.create_task(self._monitor_loop())
            logger.info("性能监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            self._monitoring_task = None
            logger.info("性能监控已停止")
    
    async def _monitor_loop(self):
        """监控循环"""
        while True:
            try:
                await asyncio.sleep(current_config.METRICS_INTERVAL_SECONDS)
                self._collect_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"监控循环出错: {e}")
    
    def _collect_metrics(self):
        """收集性能指标"""
        with self._lock:
            # 活跃会话数
            active_sessions = len(self.session_stats)
            self.metrics["active_sessions"].append({
                "timestamp": datetime.now(),
                "value": active_sessions
            })
    
    def record_request(self, session_id: str, response_time: float, success: bool = True):
        """记录请求"""
        with self._lock:
            # 记录响应时间
            self.metrics["response_times"].append({
                "timestamp": datetime.now(),
                "value": response_time
            })
            
            # 更新会话统计
            if session_id in self.session_stats:
                stats = self.session_stats[session_id]
                stats["request_count"] += 1
                stats["total_response_time"] += response_time
                stats["last_accessed"] = datetime.now()
                
                if not success:
                    stats["error_count"] += 1
                    self.metrics["error_count"].append({
                        "timestamp": datetime.now(),
                        "value": 1
                    })
    
    def create_session(self, session_id: str):
        """创建会话记录"""
        with self._lock:
            self.session_stats[session_id] = {
                "created_at": datetime.now(),
                "last_accessed": datetime.now(),
                "request_count": 0,
                "total_response_time": 0,
                "error_count": 0
            }
    
    def remove_session(self, session_id: str):
        """移除会话记录"""
        with self._lock:
            if session_id in self.session_stats:
                del self.session_stats[session_id]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        with self._lock:
            # 计算平均响应时间
            response_times = [m["value"] for m in self.metrics["response_times"]]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # 计算错误率
            total_requests = sum(stats["request_count"] for stats in self.session_stats.values())
            total_errors = sum(stats["error_count"] for stats in self.session_stats.values())
            error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "uptime_seconds": time.time() - self._start_time,
                "active_sessions": len(self.session_stats),
                "total_requests": total_requests,
                "avg_response_time_ms": round(avg_response_time * 1000, 2),
                "error_rate_percent": round(error_rate, 2),
                "system_healthy": True
            }
    
    def get_session_analytics(self) -> Dict[str, Any]:
        """获取会话分析"""
        with self._lock:
            sessions = []
            for session_id, stats in self.session_stats.items():
                avg_response_time = (
                    stats["total_response_time"] / stats["request_count"]
                    if stats["request_count"] > 0 else 0
                )
                
                sessions.append({
                    "session_id": session_id,
                    "created_at": stats["created_at"].isoformat() if stats["created_at"] else None,
                    "last_accessed": stats["last_accessed"].isoformat() if stats["last_accessed"] else None,
                    "request_count": stats["request_count"],
                    "avg_response_time_ms": round(avg_response_time * 1000, 2),
                    "error_count": stats["error_count"]
                })
            
            return {
                "total_sessions": len(sessions),
                "sessions": sessions
            }

class ConcurrencyManager:
    """并发管理器"""
    
    def __init__(self):
        self.active_sessions = set()
        self.session_locks = {}
        self._lock = threading.RLock()
        self._semaphore = asyncio.Semaphore(current_config.MAX_CONCURRENT_SESSIONS)
    
    async def acquire_session_slot(self, session_id: str) -> bool:
        """获取会话槽位"""
        try:
            await self._semaphore.acquire()
            with self._lock:
                if session_id not in self.active_sessions:
                    self.active_sessions.add(session_id)
                    self.session_locks[session_id] = threading.RLock()
                    return True
                return False
        except Exception as e:
            logger.error(f"获取会话槽位失败: {e}")
            return False
    
    def release_session_slot(self, session_id: str):
        """释放会话槽位"""
        with self._lock:
            if session_id in self.active_sessions:
                self.active_sessions.remove(session_id)
                if session_id in self.session_locks:
                    del self.session_locks[session_id]
                self._semaphore.release()
    
    def get_session_lock(self, session_id: str) -> threading.RLock:
        """获取会话锁"""
        with self._lock:
            return self.session_locks.get(session_id)
    
    def get_concurrency_stats(self) -> Dict[str, Any]:
        """获取并发统计"""
        with self._lock:
            return {
                "active_sessions": len(self.active_sessions),
                "max_concurrent_sessions": current_config.MAX_CONCURRENT_SESSIONS,
                "available_slots": self._semaphore._value,
                "session_ids": list(self.active_sessions)
            }

# 全局监控实例
performance_monitor = PerformanceMonitor()
concurrency_manager = ConcurrencyManager()

def get_monitoring_middleware():
    """获取监控中间件"""
    async def monitoring_middleware(request, call_next):
        start_time = time.time()
        session_id = request.path_params.get("session_id")
        
        try:
            response = await call_next(request)
            response_time = time.time() - start_time
            
            if session_id:
                performance_monitor.record_request(session_id, response_time, True)
            
            return response
        except Exception as e:
            response_time = time.time() - start_time
            
            if session_id:
                performance_monitor.record_request(session_id, response_time, False)
            
            raise e
    
    return monitoring_middleware
