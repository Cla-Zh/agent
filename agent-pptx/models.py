# models.py - 数据模型定义
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

class DiscussionRequest(BaseModel):
    """讨论请求模型"""
    topic: str = Field(..., min_length=1, max_length=60, description="讨论话题，最多60字")
    
    class Config:
        schema_extra = {
            "example": {
                "topic": "人工智能对未来教育的影响"
            }
        }

class DiscussionResponse(BaseModel):
    """讨论响应模型"""
    session_id: str
    status: str  # started, processing, completed, error
    message: str

class AgentResult(BaseModel):
    """Agent思考结果模型"""
    agent_key: str
    agent_name: str
    content: str
    status: str  # completed, error
    completed_at: str

class AgentStatus(BaseModel):
    """Agent状态模型"""
    agent_key: str
    agent_name: str
    status: str  # thinking, completed, error
    has_result: bool