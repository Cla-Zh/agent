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

            创业任务: {input}
            商业上下文: {context}

            请提供创新的商业解决方案：
        """
        return PromptTemplate(template)
    
    async def _postprocess_output(self, output: str) -> str:
        """后处理 - 格式化商业方案结果"""
        formatted_output = f"""
            === 商业创新方案 ===
            {output}

            === 方案完成时间 ===
            {asyncio.get_event_loop().time()}
        """
        return formatted_output.strip()

    async def think(self, topic: str) -> str:
        await self._simulate_thinking_time()
        logger.info(f"企业家Agent正在分析话题: {topic}")
        
        result = f"""# 企业家的观点

            ## 对"{topic}"的创业商业洞察

            ### 商业机会识别

            从**创业者和商业创新**的角度，我发现了巨大的商业潜力：

            🚀 **市场洞察**
            - **用户痛点**：深度挖掘未被满足的需求
            - **市场空白**：识别蓝海市场机会
            - **趋势把握**：紧跟行业发展趋势
            - **需求验证**：快速验证市场需求

            💡 **创新商业模式**

            ```
            价值主张画布：
            ┌─────────────────┬─────────────────┐
            │   价值创造      │   客户细分      │
            │ • 解决核心痛点  │ • 目标用户群体  │
            │ • 提升用户体验  │ • 用户行为特征  │
            │ • 降低使用成本  │ • 付费意愿分析  │
            └─────────────────┴─────────────────┘
            ```

            ### 创业策略

            🎯 **产品策略**
            - **MVP开发**：最小可行产品快速上市
            - **迭代优化**：基于用户反馈持续改进
            - **功能扩展**：逐步完善产品功能
            - **用户体验**：打造极致的用户体验

            📈 **增长策略**
            - **获客模式**：多渠道获客策略
            - **用户留存**：提升用户粘性和活跃度
            - **病毒传播**：设计传播机制
            - **数据驱动**：基于数据优化运营

            ### 竞争优势构建

            | 优势类型 | 具体策略 | 预期效果 |
            |---------|---------|---------|
            | 产品优势 | 技术创新 | 功能领先 |
            | 运营优势 | 效率提升 | 成本控制 |
            | 品牌优势 | 口碑营销 | 用户信任 |
            | 渠道优势 | 合作伙伴 | 市场覆盖 |

            ### 融资与扩张

            💰 **资金策略**
            - **天使轮**：验证商业模式
            - **A轮**：扩大市场份额
            - **B轮及以后**：规模化扩张

            🌍 **扩张路径**
            1. 本地市场深耕
            2. 区域市场拓展
            3. 全国市场布局
            4. 国际市场进入

            ### 创业结论

            这个领域具有**巨大的创业机会**，建议快速行动，抢占市场先机！
                    """
        
        return result.strip()
