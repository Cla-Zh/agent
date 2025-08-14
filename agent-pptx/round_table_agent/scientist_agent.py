from .agent_frm_base import AgentBase, Tool, PromptTemplate
from typing import List, Dict, Optional
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

    async def think(self, topic: str) -> str:
        await self._simulate_thinking_time()
        logger.info(f"科学家Agent正在分析话题: {topic}")
        
        result = f"""# 科学家的观点

            ## 对"{topic}"的科学分析

            ### 研究方法论
            作为科学家，我认为分析这个问题需要采用**严谨的科学方法**：

            - 🔬 **实证研究**：基于可观测的数据和现象
            - 📊 **数据驱动**：收集定量和定性数据进行分析
            - 🧪 **假设验证**：建立可测试的理论模型
            - 🔄 **同行评议**：确保研究结果的可重复性

            ### 核心观点

            从科学角度来看，"{topic}"这个问题需要我们：

            1. **建立理论框架**：基于现有科学理论构建分析模型
            2. **收集实证数据**：通过观察、实验获取可靠数据
            3. **统计分析**：运用统计学方法验证假设
            4. **控制变量**：识别和控制影响因素

            ### 科学建议

            - 采用多学科交叉的研究方法
            - 建立长期跟踪研究机制
            - 注重研究的伦理规范
            - 确保结果的社会应用价值

            ### 结论

            基于科学证据和理性分析，这个课题具有重要的研究价值，建议进行系统性的深入研究。
        """
        
        return result.strip()
   