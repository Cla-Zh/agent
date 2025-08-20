from .agent_frm_base import AgentBase, Tool, PromptTemplate
from typing import List, Dict, Optional
from agno.tools.reasoning import ReasoningTools
from agno.tools.googlesearch import GoogleSearchTools
import asyncio
import logging

logger = logging.getLogger(__name__)

class EntrepreneurAgent(AgentBase):
    """创业者Agent - 专注于商业创新和创业策略"""

    def __init__(self):
        from .agent_frm_base import AgentConfig, AgentType
        config = AgentConfig(
            name="企业家",
            agent_type=AgentType.ENTREPRENEUR
        )
        super().__init__(config, "企业家", "企业家")
    
    def _setup_tools(self) -> List[Tool]:
        """设置商业创新相关工具"""
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
        """设置创业者提示模板"""
        template = """
            你是一个富有远见的创业者。你擅长：

            1. 市场机会识别和商业洞察
            2. 商业模式设计和创新
            3. 商业计划制定和战略规划
            4. 风险评估和投资决策

            要求：基于用户给定的任务与可选上下文，提供创新的商业分析和解决方案，包括：市场机会、商业模式、创新策略、风险评估、发展路径等。
        """
        return PromptTemplate(template)
    
    async def _postprocess_output(self, output: str) -> str:
        """后处理 - 格式化商业方案结果"""
        formatted_output = f"""
            === 商业创新方案 ===
            {output}
        """
        return formatted_output.strip()

    async def think(self, topic: str) -> str:
        await self._simulate_thinking_time()
        logger = self.get_logger()
        logger.info(f"创业者Agent正在分析话题: {topic}")
        
        # 使用基类的process方法进行实际推理
        result = await self.process(topic)
        
        return result.strip()
