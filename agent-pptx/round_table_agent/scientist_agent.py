from .agent_frm_base import AgentBase, Tool, PromptTemplate
from typing import List, Dict, Optional
from agno.tools.reasoning import ReasoningTools
from agno.tools.googlesearch import GoogleSearchTools
import asyncio
import logging

logger = logging.getLogger(__name__)

class ScientistAgent(AgentBase):
    """科学家Agent - 专注于科学研究和技术创新"""

    def __init__(self):
        from .agent_frm_base import AgentConfig, AgentType
        config = AgentConfig(
            name="科学家",
            agent_type=AgentType.SCIENTIST
        )
        super().__init__(config, "科学家", "科学家")
    
    def _setup_tools(self) -> List[Tool]:
        """设置科学研究相关工具"""
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
        """设置科学家提示模板"""
        template = """
            你是一个资深的科学家。你擅长：

            1. 科学研究和实验设计
            2. 数据分析和模型构建
            3. 文献综述和理论分析
            4. 技术创新和问题解决

            要求：基于用户给定的任务与可选上下文，运用科学方法进行严谨的分析，包括：研究假设、实验设计、数据分析、理论验证、结论推导等。
        """
        return PromptTemplate(template)
    
    async def _preprocess_input(self, input_text: str, context: Optional[Dict] = None) -> str:
        """预处理 - 添加科学研究关键词识别"""
        research_keywords = ["研究", "实验", "分析", "科学", "技术", "创新"]
        if any(keyword in input_text for keyword in research_keywords):
            return f"[科学研究模式] {input_text}"
        return input_text
    
    async def _postprocess_output(self, output: str) -> str:
        """后处理 - 格式化科学研究结果"""
        formatted_output = f"""
            === 科学研究报告 ===
            {output}
        """
        return formatted_output.strip()

    async def think(self, topic: str) -> str:
        await self._simulate_thinking_time()
        logger = self.get_logger()
        logger.info(f"科学家Agent正在分析话题: {topic}")
        
        # 使用基类的process方法进行实际推理
        result = await self.process(topic)
        
        return result.strip()
   