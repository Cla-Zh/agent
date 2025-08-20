# main_optimized.py - 优化后的FastAPI主服务器
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
import uuid
from typing import Dict, List
import json
from datetime import datetime, timedelta
import logging
import threading
from contextlib import asynccontextmanager

from agents import AgentManager
from models import DiscussionRequest, DiscussionResponse, AgentResult
from round_table_agent.artist_agent import ArtistAgent
from round_table_agent.entrepreneur_agent import EntrepreneurAgent
from round_table_agent.financier_agent import FinancierAgent
from round_table_agent.manager_agent import ManagerAgent
from round_table_agent.scientist_agent import ScientistAgent
from round_table_agent.software_architect_agent import SoftwareArchitectAgent

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 线程安全的会话存储
class ThreadSafeDiscussionStore:
    """线程安全的讨论会话存储"""
    
    def __init__(self):
        self._discussions: Dict[str, Dict] = {}
        self._lock = threading.RLock()
    
    def create_session(self, session_id: str, topic: str) -> None:
        """创建新的讨论会话"""
        with self._lock:
            self._discussions[session_id] = {
                "topic": topic,
                "status": "processing",
                "created_at": datetime.now(),
                "results": {},
                "completed_agents": [],
                "last_accessed": datetime.now()
            }
    
    def get_session(self, session_id: str) -> Dict:
        """获取会话数据"""
        with self._lock:
            if session_id in self._discussions:
                self._discussions[session_id]["last_accessed"] = datetime.now()
                return self._discussions[session_id].copy()
            return None
    
    def update_session(self, session_id: str, updates: Dict) -> None:
        """更新会话数据"""
        with self._lock:
            if session_id in self._discussions:
                self._discussions[session_id].update(updates)
                self._discussions[session_id]["last_accessed"] = datetime.now()
    
    def delete_session(self, session_id: str) -> None:
        """删除会话"""
        with self._lock:
            if session_id in self._discussions:
                del self._discussions[session_id]
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24) -> None:
        """清理过期的会话"""
        with self._lock:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            expired_sessions = [
                session_id for session_id, data in self._discussions.items()
                if data["last_accessed"] < cutoff_time
            ]
            
            for session_id in expired_sessions:
                del self._discussions[session_id]
                logger.info(f"清理过期会话: {session_id}")
            
            if expired_sessions:
                logger.info(f"清理了 {len(expired_sessions)} 个过期会话")

# 线程安全的Agent管理器
class ThreadSafeAgentManager:
    """线程安全的Agent管理器，为每个会话创建独立的Agent实例"""
    
    def __init__(self):
        self._agent_factories = {
            "scientist": ScientistAgent,
            "financier": FinancierAgent,
            "engineer": SoftwareArchitectAgent,
            "leader": ManagerAgent,
            "entrepreneur": EntrepreneurAgent,
            "artist": ArtistAgent
        }
        self._session_agents: Dict[str, Dict[str, object]] = {}
        self._lock = threading.RLock()
    
    def get_agents_for_session(self, session_id: str) -> Dict[str, object]:
        """为指定会话获取Agent实例"""
        with self._lock:
            if session_id not in self._session_agents:
                # 为每个会话创建独立的Agent实例
                self._session_agents[session_id] = {
                    key: factory_class() 
                    for key, factory_class in self._agent_factories.items()
                }
                logger.info(f"为会话 {session_id} 创建了 {len(self._agent_factories)} 个Agent实例")
            
            return self._session_agents[session_id]
    
    def cleanup_session_agents(self, session_id: str) -> None:
        """清理指定会话的Agent实例"""
        with self._lock:
            if session_id in self._session_agents:
                del self._session_agents[session_id]
                logger.info(f"清理会话 {session_id} 的Agent实例")

# 全局实例
discussion_store = ThreadSafeDiscussionStore()
agent_manager = ThreadSafeAgentManager()

# 启动时清理任务
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("启动AI Agent讨论系统...")
    cleanup_task = asyncio.create_task(periodic_cleanup())
    yield
    cleanup_task.cancel()
    logger.info("关闭AI Agent讨论系统...")

app = FastAPI(
    title="AI Agent Discussion System", 
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

async def periodic_cleanup():
    """定期清理过期会话和Agent实例"""
    while True:
        try:
            await asyncio.sleep(3600)  # 每小时清理一次
            discussion_store.cleanup_expired_sessions()
            logger.info("定期清理任务执行完成")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"定期清理任务出错: {e}")

@app.get("/")
async def read_index():
    """提供前端页面"""
    from fastapi.responses import FileResponse
    return FileResponse('static/index.html')

@app.post("/api/discuss", response_model=DiscussionResponse)
async def start_discussion(request: DiscussionRequest):
    """开始AI Agent讨论"""
    try:
        session_id = str(uuid.uuid4())
        discussion_store.create_session(session_id, request.topic)
        
        logger.info(f"开始新讨论会话: {session_id}, 话题: {request.topic}")
        
        # 启动异步思考任务
        asyncio.create_task(process_discussion(session_id, request.topic))
        
        return DiscussionResponse(
            session_id=session_id,
            status="started",
            message="讨论已开始，各Agent正在思考中..."
        )
        
    except Exception as e:
        logger.error(f"启动讨论失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动讨论失败: {str(e)}")

@app.get("/api/discuss/{session_id}/status")
async def get_discussion_status(session_id: str):
    """获取讨论状态和结果"""
    discussion = discussion_store.get_session(session_id)
    if not discussion:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    return {
        "session_id": session_id,
        "status": discussion["status"],
        "topic": discussion["topic"],
        "results": discussion["results"],
        "completed_agents": discussion["completed_agents"],
        "total_agents": len(agent_manager._agent_factories),
        "progress": len(discussion["completed_agents"]) / len(agent_manager._agent_factories)
    }

@app.get("/api/discuss/{session_id}/result/{agent_key}")
async def get_agent_result(session_id: str, agent_key: str):
    """获取特定Agent的思考结果"""
    discussion = discussion_store.get_session(session_id)
    if not discussion:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    if agent_key not in discussion["results"]:
        raise HTTPException(status_code=404, detail="该Agent尚未完成思考")
    
    return discussion["results"][agent_key]

@app.delete("/api/discuss/{session_id}")
async def delete_discussion(session_id: str):
    """删除讨论会话"""
    discussion = discussion_store.get_session(session_id)
    if not discussion:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    # 清理会话数据和Agent实例
    discussion_store.delete_session(session_id)
    agent_manager.cleanup_session_agents(session_id)
    
    return {"message": "会话已删除"}

async def process_discussion(session_id: str, topic: str):
    """异步处理讨论 - 多Agent并发思考"""
    try:
        logger.info(f"开始处理讨论 {session_id}: {topic}")
        
        # 获取该会话专用的Agent实例
        agents = agent_manager.get_agents_for_session(session_id)
        
        # 创建异步任务列表
        tasks = []
        for agent_key, agent in agents.items():
            task = asyncio.create_task(
                run_agent_thinking(session_id, agent_key, agent, topic)
            )
            tasks.append(task)
        
        # 等待所有Agent完成思考
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                agent_key = list(agents.keys())[i]
                logger.error(f"Agent {agent_key} 执行异常: {result}")
        
        # 更新讨论状态为完成
        discussion_store.update_session(session_id, {"status": "completed"})
        logger.info(f"讨论 {session_id} 已完成")
        
    except Exception as e:
        logger.error(f"讨论处理错误: {e}")
        discussion_store.update_session(session_id, {"status": "error"})

async def run_agent_thinking(session_id: str, agent_key: str, agent, topic: str):
    """运行单个Agent的思考过程"""
    try:
        logger.info(f"Agent {agent_key} 开始思考话题: {topic}")
        
        # 调用Agent的思考方法
        result = await agent.think(topic)
        
        # 保存结果
        result_data = {
            "agent_key": agent_key,
            "agent_name": agent.role,
            "content": result,
            "status": "completed",
            "completed_at": datetime.now().isoformat()
        }
        
        # 更新会话数据
        discussion = discussion_store.get_session(session_id)
        if discussion:
            discussion["results"][agent_key] = result_data
            discussion["completed_agents"].append(agent_key)
            discussion_store.update_session(session_id, {
                "results": discussion["results"],
                "completed_agents": discussion["completed_agents"]
            })
        
        logger.info(f"Agent {agent_key} 思考完成")
        
    except Exception as e:
        logger.error(f"Agent {agent_key} 思考错误: {e}")
        
        error_data = {
            "agent_key": agent_key,
            "agent_name": getattr(agent, 'role', agent_key),
            "content": f"思考过程中出现错误: {str(e)}",
            "status": "error",
            "completed_at": datetime.now().isoformat()
        }
        
        # 更新会话数据
        discussion = discussion_store.get_session(session_id)
        if discussion:
            discussion["results"][agent_key] = error_data
            discussion["completed_agents"].append(agent_key)
            discussion_store.update_session(session_id, {
                "results": discussion["results"],
                "completed_agents": discussion["completed_agents"]
            })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
