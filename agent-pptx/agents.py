# agents.py - Agent管理器和具体Agent实现
import asyncio
import random
from abc import ABC, abstractmethod
from typing import Dict, List
import logging
from round_table_agent.agent_frm_base import AgentBase as BaseAgent
from round_table_agent.scientist_agent import ScientistAgent
from round_table_agent.financier_agent import FinancierAgent
from round_table_agent.software_architect_agent import SoftwareArchitectAgent
from round_table_agent.manager_agent import ManagerAgent
from round_table_agent.entrepreneur_agent import EntrepreneurAgent
from round_table_agent.artist_agent import ArtistAgent

logger = logging.getLogger(__name__)


class AgentManager:
    """Agent管理器"""
    
    def __init__(self):
        self.agents = {
            "scientist": ScientistAgent(),
            "financier": FinancierAgent(), 
            "engineer": SoftwareArchitectAgent(),
            "leader": ManagerAgent(),
            "entrepreneur": EntrepreneurAgent(),
            "artist": ArtistAgent()
        }
        logger.info(f"初始化完成，共加载 {len(self.agents)} 个Agent")
    
    def get_all_agents(self) -> Dict[str, BaseAgent]:
        """获取所有Agent"""
        return self.agents
    
    def get_agent(self, agent_key: str) -> BaseAgent:
        """获取特定Agent"""
        return self.agents.get(agent_key)
    
    def get_agent_keys(self) -> List[str]:
        """获取所有Agent的键"""
        return list(self.agents.keys())
    
    async def run_all_agents(self, topic: str) -> Dict[str, str]:
        """并发运行所有Agent（测试用）"""
        tasks = []
        for agent_key, agent in self.agents.items():
            task = asyncio.create_task(agent.think(topic))
            tasks.append((agent_key, task))
        
        results = {}
        for agent_key, task in tasks:
            try:
                result = await task
                results[agent_key] = result
            except Exception as e:
                logger.error(f"Agent {agent_key} 执行失败: {e}")
                results[agent_key] = f"思考过程中出现错误: {str(e)}"
        
        return results