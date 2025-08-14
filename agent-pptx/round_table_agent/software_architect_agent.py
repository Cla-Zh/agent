from agent_frm_base import AgentBase, Tool, PromptTemplate
from typing import List, Dict, Optional
import asyncio

class SoftwareArchitectAgent(AgentBase):
    """软件架构师Agent - 专注于系统设计和架构规划"""
    
    def _setup_tools(self) -> List[Tool]:
        """设置软件架构相关工具"""
        tools = []
        try:
            tools.extend([
                # SystemDesignTool(),
                # ArchitecturePatternTool(),
                # PerformanceAnalysisTool(),
                # ScalabilityPlanningTool()
            ])
        except:
            # 模拟工具
            tools = [Tool(), Tool(), Tool(), Tool()]
        
        self.logger.info(f"SoftwareArchitectAgent加载了{len(tools)}个工具")
        return tools
    
    def _setup_prompt(self) -> PromptTemplate:
        """设置软件架构师提示模板"""
        template = """
            你是一个资深的软件架构师。你擅长：

            1. 系统架构设计和规划
            2. 技术选型和架构模式应用
            3. 性能优化和可扩展性设计
            4. 技术风险评估和解决方案

            架构设计任务: {input}
            技术上下文: {context}

            请提供专业的软件架构设计方案：
        """
        return PromptTemplate(template)
    
    async def _preprocess_input(self, input_text: str, context: Optional[Dict] = None) -> str:
        """预处理 - 识别架构设计需求类型"""
        architecture_keywords = {
            "架构": "架构设计",
            "系统": "系统设计",
            "微服务": "微服务架构",
            "分布式": "分布式系统",
            "性能": "性能优化",
            "扩展": "可扩展性"
        }
        
        for keyword, label in architecture_keywords.items():
            if keyword in input_text:
                return f"[{label}模式] {input_text}"
        
        return f"[软件架构模式] {input_text}"
    
    async def _postprocess_output(self, output: str) -> str:
        """后处理 - 格式化架构设计方案结果"""
        formatted_output = f"""
            === 软件架构设计方案 ===
            {output}

            === 方案完成时间 ===
            {asyncio.get_event_loop().time()}
        """
        return formatted_output.strip()
