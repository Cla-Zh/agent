
from agent_frm_base import AgentBase, Tool, PromptTemplate
from typing import List, Dict, Optional
import asyncio

class EntrepreneurAgent(AgentBase):
    """创业者Agent - 专注于商业创新和创业策略"""
    
    def _setup_tools(self) -> List[Tool]:
        """设置商业创新相关工具"""
        tools = []
        try:
            tools.extend([
                # MarketAnalysisTool(),
                # BusinessPlanGeneratorTool(),
                # FinancialProjectionTool(),
                # CompetitiveAnalysisTool()
            ])
        except:
            # 模拟工具
            tools = [Tool(), Tool(), Tool(), Tool()]
        
        self.logger.info(f"EntrepreneurAgent加载了{len(tools)}个工具")
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
