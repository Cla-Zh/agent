from .agent_frm_base import AgentBase, Tool, PromptTemplate
from typing import List, Dict, Optional
from agno.tools.reasoning import ReasoningTools
from agno.tools.googlesearch import GoogleSearchTools
import asyncio
import logging
import json

logger = logging.getLogger(__name__)

class SoftwareArchitectAgent(AgentBase):
    """软件架构师Agent - 专注于系统设计和架构规划"""

    def __init__(self):
        from .agent_frm_base import AgentConfig, AgentType
        config = AgentConfig(
            name="软件架构师",
            agent_type=AgentType.ENGINEER
        )
        super().__init__(config, "软件架构师", "软件架构师")
    
    def _setup_tools(self) -> List[Tool]:
        """设置软件架构相关工具"""
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
        """设置软件架构师提示模板"""
        template = """
            你是一个资深的软件架构师。你擅长：

            1. 系统架构设计和规划
            2. 技术选型和架构模式应用
            3. 性能优化和可扩展性设计
            4. 技术风险评估和解决方案

            要求：基于用户给定的任务与可选上下文，输出可执行的架构设计与技术方案，包括：总体架构、关键组件、数据流、技术选型、扩展性与可靠性设计、风险与权衡、里程碑与落地建议。
        """
        return PromptTemplate(template)
    
    async def _preprocess_input(self, input_text: str, context: Optional[Dict] = None) -> str:
        """预处理 - 识别架构设计需求类型，并合并上下文信息"""
        architecture_keywords = {
            "架构": "架构设计",
            "系统": "系统设计",
            "微服务": "微服务架构",
            "分布式": "分布式系统",
            "性能": "性能优化",
            "扩展": "可扩展性"
        }
        
        label_detected = "软件架构模式"
        for keyword, label in architecture_keywords.items():
            if keyword in input_text:
                label_detected = f"{label}模式"
                break

        context_text = ""
        if context is not None:
            try:
                if isinstance(context, (dict, list)):
                    context_text = "\n技术上下文:" + json.dumps(context, ensure_ascii=False)
                else:
                    context_text = f"\n技术上下文:{context}"
            except Exception:
                context_text = f"\n技术上下文:{str(context)}"

        return f"[{label_detected}] 架构设计任务:{input_text}{context_text}"
    
    async def _postprocess_output(self, output: str) -> str:
        """后处理 - 格式化架构设计方案结果"""
        formatted_output = f"""
            === 软件架构设计方案 ===
            {output}
        """
        return formatted_output.strip()

    async def think(self, topic: str) -> str:
        await self._simulate_thinking_time()
        logger = self.get_logger()
        logger.info(f"软件架构师Agent正在分析话题: {topic}")
        
        # 使用基类的process方法进行实际推理
        result = await self.process(topic)
        
        return result.strip()
