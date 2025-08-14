
from agent_frm_base import AgentBase, Tool, PromptTemplate
from typing import List, Dict, Optional
import asyncio

class FinancierAgent(AgentBase):
    """金融家Agent - 专注于金融分析和投资决策"""
    
    def _setup_tools(self) -> List[Tool]:
        """设置金融分析相关工具"""
        tools = []
        try:
            tools.extend([
                # FinancialAnalysisTool(),
                # InvestmentPortfolioTool(),
                # RiskAssessmentTool(),
                # MarketTrendAnalysisTool()
            ])
        except:
            # 模拟工具
            tools = [Tool(), Tool(), Tool(), Tool()]
        
        self.logger.info(f"FinancierAgent加载了{len(tools)}个工具")
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
