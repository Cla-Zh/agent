
from .agent_frm_base import AgentBase, Tool, PromptTemplate
from typing import List, Dict, Optional
from agno.tools.reasoning import ReasoningTools
from agno.tools.googlesearch import GoogleSearchTools
import asyncio
import logging

logger = logging.getLogger(__name__)

class FinancierAgent(AgentBase):
    """金融家Agent - 专注于金融分析和投资决策"""

    def __init__(self):
        from .agent_frm_base import AgentConfig, AgentType
        config = AgentConfig(
            name="金融家",
            agent_type=AgentType.FINANCIER
        )
        super().__init__(config, "金融家", "金融家")
    
    def _setup_tools(self) -> List[Tool]:
        """设置金融分析相关工具"""
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
        """设置金融家提示模板"""
        template = """
            你是一个资深的金融分析师。你擅长：

            1. 财务分析和投资评估
            2. 风险评估和投资组合管理
            3. 市场趋势分析和预测
            4. 投资策略制定和决策

            要求：基于用户给定的任务与可选上下文，提供专业的金融分析和投资建议，包括：市场分析、风险评估、投资策略、财务预测、决策建议等。
        """
        return PromptTemplate(template)
    
    async def _postprocess_output(self, output: str) -> str:
        """后处理 - 格式化金融分析结果"""
        formatted_output = f"""
            === 金融分析报告 ===
            {output}
        """
        return formatted_output.strip()
    
    async def think(self, topic: str) -> str:
        await self._simulate_thinking_time()
        logger.info(f"金融家Agent正在分析话题: {topic}")
        
        # 使用基类的process方法进行实际推理
        result = await self.process(topic)
        
        return result.strip()
