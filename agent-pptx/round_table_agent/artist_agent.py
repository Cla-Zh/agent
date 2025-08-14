from agent_frm_base import AgentBase, Tool, PromptTemplate
from typing import List, Dict, Optional
import asyncio

class ArtistAgent(AgentBase):
    """艺术家Agent - 专注于创意设计和美学表达"""
    
    def _setup_tools(self) -> List[Tool]:
        """设置艺术创作相关工具"""
        tools = []
        try:
            tools.extend([
                # ImageGenerationTool(),
                # ColorPaletteTool(),
                # DesignPatternTool(),
                # CreativeWritingTool()
            ])
        except:
            # 模拟工具
            tools = [Tool(), Tool(), Tool(), Tool()]
        
        self.logger.info(f"ArtistAgent加载了{len(tools)}个工具")
        return tools
    
    def _setup_prompt(self) -> PromptTemplate:
        """设置艺术家提示模板"""
        template = """
            你是一个富有创造力的艺术家。你擅长：

            1. 视觉艺术设计和创意表达
            2. 色彩搭配和美学设计
            3. 创意写作和故事创作
            4. 艺术风格分析和创新

            创作任务: {input}
            艺术上下文: {context}

            请提供富有创意的艺术设计方案：
        """
        return PromptTemplate(template)
    
    async def _postprocess_output(self, output: str) -> str:
        """后处理 - 格式化艺术创作结果"""
        formatted_output = f"""
            === 艺术创作方案 ===
            {output}

            === 创作完成时间 ===
            {asyncio.get_event_loop().time()}
        """
        return formatted_output.strip()
