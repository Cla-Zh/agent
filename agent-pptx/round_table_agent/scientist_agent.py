from agent_frm_base import AgentBase, Tool, PromptTemplate
from typing import List, Dict, Optional
import asyncio

class ScientistAgent(AgentBase):
    """科学家Agent - 专注于科学研究和技术创新"""
    
    def _setup_tools(self) -> List[Tool]:
        """设置科学研究相关工具"""
        tools = []
        try:
            tools.extend([
                # ScientificResearchTool(),
                # ExperimentDesignTool(),
                # DataAnalysisTool(),
                # LiteratureReviewTool()
            ])
        except:
            # 模拟工具
            tools = [Tool(), Tool(), Tool(), Tool()]
        
        self.logger.info(f"ScientistAgent加载了{len(tools)}个工具")
        return tools
    
    def _setup_prompt(self) -> PromptTemplate:
        """设置科学家提示模板"""
        template = """
            你是一个资深的科学家。你擅长：

            1. 科学研究和实验设计
            2. 数据分析和模型构建
            3. 文献综述和理论分析
            4. 技术创新和问题解决

            研究任务: {input}
            科学上下文: {context}

            请基于科学方法，提供严谨的研究分析：
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

            === 研究完成时间 ===
            {asyncio.get_event_loop().time()}
        """
        return formatted_output.strip()
