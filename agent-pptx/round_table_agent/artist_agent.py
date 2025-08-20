from .agent_frm_base import AgentBase, Tool, PromptTemplate
from typing import List, Dict, Optional
from agno.tools.reasoning import ReasoningTools
from agno.tools.googlesearch import GoogleSearchTools
import asyncio
import logging

logger = logging.getLogger(__name__)

class ArtistAgent(AgentBase):
    """艺术家Agent - 专注于创意设计和美学表达"""

    def __init__(self):
        from .agent_frm_base import AgentConfig, AgentType
        config = AgentConfig(
            name="艺术家",
            agent_type=AgentType.ARTIST
        )
        super().__init__(config, "艺术家", "艺术家")
    
    def _setup_tools(self) -> List[Tool]:
        """设置艺术创作相关工具"""
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
        """设置艺术家提示模板"""
        template = """
            你是一个富有创造力的艺术家。你擅长：

            1. 视觉艺术设计和创意表达
            2. 色彩搭配和美学设计
            3. 创意写作和故事创作
            4. 艺术风格分析和创新

            要求：基于用户给定的任务与可选上下文，提供富有创意的艺术分析和设计方案，包括：美学视角、创意表达、视觉设计、用户体验、艺术价值等。
        """
        return PromptTemplate(template)
    
    async def _postprocess_output(self, output: str) -> str:
        """后处理 - 格式化艺术创作结果"""
        formatted_output = f"""
            === 艺术创作方案 ===
            {output}
        """
        return formatted_output.strip()
        
    async def think(self, topic: str) -> str:
        await self._simulate_thinking_time()
        logger.info(f"艺术家Agent正在分析话题: {topic}")
        
        # 使用基类的process方法进行实际推理
        result = await self.process(topic)
        
        return result.strip()
    