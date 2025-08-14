from agent_frm_base import AgentBase, Tool, PromptTemplate
from typing import List, Dict, Optional
import asyncio

class ManagerAgent(AgentBase):
    """管理者Agent - 专注于项目管理和团队协调"""
    
    def _setup_tools(self) -> List[Tool]:
        """设置项目管理相关工具"""
        tools = []
        try:
            tools.extend([
                # ProjectManagementTool(),
                # TeamCoordinationTool(),
                # ResourceAllocationTool(),
                # ProgressTrackingTool()
            ])
        except:
            # 模拟工具
            tools = [Tool(), Tool(), Tool(), Tool()]
        
        self.logger.info(f"ManagerAgent加载了{len(tools)}个工具")
        return tools
    
    def _setup_prompt(self) -> PromptTemplate:
        """设置管理者提示模板"""
        template = """
            你是一个经验丰富的项目管理者。你擅长：

            1. 项目规划和目标设定
            2. 团队协调和资源分配
            3. 进度跟踪和风险管理
            4. 沟通协调和决策制定

            管理任务: {input}
            项目上下文: {context}

            请提供专业的管理方案和决策建议：
        """
        return PromptTemplate(template)
    
    async def _postprocess_output(self, output: str) -> str:
        """后处理 - 格式化管理方案结果"""
        formatted_output = f"""
            === 项目管理方案 ===
            {output}

            === 方案完成时间 ===
            {asyncio.get_event_loop().time()}
        """
        return formatted_output.strip()