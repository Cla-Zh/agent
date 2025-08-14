# main.py - FastAPI主服务器
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
import uuid
from typing import Dict, List
import json
from datetime import datetime
import logging

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

app = FastAPI(title="AI Agent Discussion System", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务（用于前端页面）
app.mount("/static", StaticFiles(directory="static"), name="static")

# 全局Agent管理器
agent_manager = AgentManager()

# 存储讨论会话
discussions: Dict[str, Dict] = {}

@app.get("/")
async def read_index():
    """提供前端页面"""
    from fastapi.responses import FileResponse
    return FileResponse('static/index.html')

@app.post("/api/discuss", response_model=DiscussionResponse)
async def start_discussion(request: DiscussionRequest):
    """
    开始AI Agent讨论
    """
    try:
        # 生成会话ID
        session_id = str(uuid.uuid4())
        
        # 初始化讨论会话
        discussions[session_id] = {
            "topic": request.topic,
            "status": "processing",
            "created_at": datetime.now(),
            "results": {},
            "completed_agents": []
        }
        
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
    """
    获取讨论状态和结果
    """
    if session_id not in discussions:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    discussion = discussions[session_id]
    
    return {
        "session_id": session_id,
        "status": discussion["status"],
        "topic": discussion["topic"],
        "results": discussion["results"],
        "completed_agents": discussion["completed_agents"],
        "total_agents": len(agent_manager.get_all_agents()),
        "progress": len(discussion["completed_agents"]) / len(agent_manager.get_all_agents())
    }

@app.get("/api/discuss/{session_id}/result/{agent_key}")
async def get_agent_result(session_id: str, agent_key: str):
    """
    获取特定Agent的思考结果
    """
    if session_id not in discussions:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    discussion = discussions[session_id]
    
    if agent_key not in discussion["results"]:
        raise HTTPException(status_code=404, detail="该Agent尚未完成思考")
    
    return discussion["results"][agent_key]

async def process_discussion(session_id: str, topic: str):
    """
    异步处理讨论 - 多Agent并发思考
    """
    try:
        logger.info(f"开始处理讨论 {session_id}: {topic}")
        
        # 获取所有Agent
        agents = agent_manager.get_all_agents()
        
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
        discussions[session_id]["status"] = "completed"
        logger.info(f"讨论 {session_id} 已完成")
        
    except Exception as e:
        logger.error(f"讨论处理错误: {e}")
        discussions[session_id]["status"] = "error"

async def run_agent_thinking(session_id: str, agent_key: str, agent, topic: str):
    """
    运行单个Agent的思考过程
    """
    try:
        logger.info(f"Agent {agent_key} 开始思考话题: {topic}")
        
        # 调用Agent的思考方法
        result = await agent.think(topic)
        
        # 保存结果
        discussions[session_id]["results"][agent_key] = {
            "agent_key": agent_key,
            "agent_name": agent.role,
            "content": result,
            "status": "completed",
            "completed_at": datetime.now().isoformat()
        }
        
        # 添加到已完成列表
        discussions[session_id]["completed_agents"].append(agent_key)
        
        logger.info(f"Agent {agent_key} 思考完成")
        
    except Exception as e:
        logger.error(f"Agent {agent_key} 思考错误: {e}")
        discussions[session_id]["results"][agent_key] = {
            "agent_key": agent_key,
            "agent_name": getattr(agent, 'role', agent_key),
            "content": f"思考过程中出现错误: {str(e)}",
            "status": "error",
            "completed_at": datetime.now().isoformat()
        }
        discussions[session_id]["completed_agents"].append(agent_key)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)