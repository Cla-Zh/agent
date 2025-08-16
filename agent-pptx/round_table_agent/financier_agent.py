
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

            金融分析任务: {input}
            市场上下文: {context}

            请提供专业的金融分析和投资建议：
        """
        return PromptTemplate(template)
    
    async def _postprocess_output(self, output: str) -> str:
        """后处理 - 格式化金融分析结果"""
        formatted_output = f"""
            === 金融分析报告 ===
            {output}

            === 分析完成时间 ===
            {asyncio.get_event_loop().time()}
        """
        return formatted_output.strip()
    
    async def think(self, topic: str) -> str:
        await self._simulate_thinking_time()
        logger.info(f"金融家Agent正在分析话题: {topic}")
        
        result = f"""# 金融家的观点

            ## 对"{topic}"的投资与财务分析

            ### 市场机会评估
            从**投资和资本市场**的视角分析，我看到以下机会：

            💰 **投资价值**
            - 市场规模潜力巨大
            - 具备长期增长动力
            - 符合未来发展趋势

            📈 **商业模式分析**
            - **收入模式**：多元化收入来源
            - **成本结构**：可控的运营成本
            - **盈利能力**：良好的利润率预期

            ### 风险评估矩阵

            | 风险类型 | 概率 | 影响度 | 应对策略 |
            |---------|------|--------|---------|
            | 市场风险 | 中等 | 高 | 分散投资组合 |
            | 政策风险 | 低 | 中 | 密切关注政策变化 |
            | 技术风险 | 中等 | 中 | 技术储备与创新 |
            | 竞争风险 | 高 | 高 | 建立护城河 |

            ### 财务建议

            1. **资金配置**：建议采用阶段性投资策略
            2. **现金流管理**：确保充足的运营资金
            3. **风险对冲**：建立完善的风险管理体系
            4. **退出机制**：制定清晰的退出策略

            ### 投资结论

            从财务角度看，这是一个**值得关注的投资机会**，建议进行深度尽职调查后考虑投资。
        """
        
        return result.strip()
