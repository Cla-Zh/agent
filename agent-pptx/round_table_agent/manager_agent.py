from .agent_frm_base import AgentBase, Tool, PromptTemplate
from typing import List, Dict, Optional
from agno.tools.reasoning import ReasoningTools
from agno.tools.googlesearch import GoogleSearchTools
import asyncio
import logging

logger = logging.getLogger(__name__)

class ManagerAgent(AgentBase):
    """管理者Agent - 专注于项目管理和团队协调"""

    def __init__(self):
        from .agent_frm_base import AgentConfig, AgentType
        config = AgentConfig(
            name="领导者",
            agent_type=AgentType.LEADER
        )
        super().__init__(config, "领导者", "领导者")
    
    def _setup_tools(self) -> List[Tool]:
        """设置项目管理相关工具"""
        tools = []
        try:
            tools=[
                    ReasoningTools(add_instructions=True),
                    GoogleSearchTools(),
                ]
        except Exception as e:
            self.logger.error(f"工具初始化失败: {str(e)}")
        return tools
    
    def _setup_prompt(self) -> PromptTemplate:
        """设置管理者提示模板"""
        template = """
            你是一个经验丰富的项目管理者。你擅长：

            1. 项目规划和目标设定
            2. 团队协调和资源分配
            3. 进度跟踪和风险管理
            4. 沟通协调和决策制定

            要求：基于用户给定的任务与可选上下文，提供专业的管理分析和决策建议，包括：战略规划、团队管理、资源配置、风险控制、执行路径等。
        """
        return PromptTemplate(template)
    
    async def _postprocess_output(self, output: str) -> str:
        """后处理 - 格式化管理方案结果"""
        formatted_output = f"""
            === 项目管理方案 ===
            {output}
        """
        return formatted_output.strip()

    async def think(self, topic: str) -> str:
        await self._simulate_thinking_time()
        logger = self.get_logger()
        logger.info(f"管理者Agent正在分析话题: {topic}")
        
        # 使用基类的process方法进行实际推理
        result = await self.process(topic)
        
        return result.strip()
