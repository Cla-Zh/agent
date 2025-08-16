from .agent_frm_base import AgentBase, Tool, PromptTemplate
from typing import List, Dict, Optional
from agno.tools.reasoning import ReasoningTools
from agno.tools.googlesearch import GoogleSearchTools
import asyncio
import logging

logger = logging.getLogger(__name__)

class ArtistAgent(AgentBase):
    """艺术家Agent - 专注于创意设计和美学表达"""

    def __init__(self):
        from .agent_frm_base import AgentConfig, AgentType
        config = AgentConfig(
            name="艺术家",
            agent_type=AgentType.ARTIST
        )
        super().__init__(config, "艺术家", "艺术家")
    
    def _setup_tools(self) -> List[Tool]:
        """设置艺术创作相关工具"""
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
        
    async def think(self, topic: str) -> str:
        await self._simulate_thinking_time()
        logger.info(f"艺术家Agent正在分析话题: {topic}")
        
        result = f"""# 艺术家的观点

            ## 对"{topic}"的创意美学思考

            ### 美学视角解析

            从**艺术和设计**的角度，这个话题激发了我的无限创意灵感：

            🎨 **视觉美学**
            - **色彩心理学**：运用色彩传达情感
            - **构图原理**：平衡、对比、韵律的运用
            - **视觉层次**：信息的视觉化呈现
            - **品牌形象**：独特的视觉识别系统

            ✨ **用户体验设计**

            ```
            设计思维流程：
            共情 → 定义 → 构思 → 原型 → 测试
            ↓      ↓      ↓      ↓      ↓
            理解   洞察   创意   验证   优化
            ```

            ### 创意表现形式

            🎭 **情感体验设计**
            - **情感连接**：与用户建立深层情感共鸣
            - **故事叙述**：通过叙事增强用户参与感
            - **互动体验**：设计有趣的交互方式
            - **感官体验**：多感官融合的体验设计

            🖼️ **视觉传达策略**

            | 设计元素 | 应用方向 | 预期效果 |
            |---------|---------|---------|
            | 色彩搭配 | 品牌调性 | 情感传达 |
            | 字体设计 | 信息层次 | 可读性提升 |
            | 图形符号 | 概念表达 | 理解便捷 |
            | 动效设计 | 交互反馈 | 体验流畅 |

            ### 艺术创新理念

            🌈 **跨界融合**
            - **科技+艺术**：数字艺术的创新表达
            - **传统+现代**：文化传承与现代演绎
            - **虚拟+现实**：沉浸式体验设计
            - **个人+群体**：社交化艺术创作

            🎪 **体验场景设计**
            - **沉浸式环境**：创造身临其境的感受
            - **互动装置**：鼓励用户主动参与
            - **多媒体融合**：视听触嗅的全方位体验
            - **情境化设计**：符合使用场景的设计

            ### 美学价值主张

            💫 **设计哲学**
            > "好的设计不仅是功能的实现，更是情感的传达和价值的体现"

            🎨 **创意建议**
            1. **以人为本**：始终将用户体验放在首位
            2. **简约美学**：在简洁中体现优雅
            3. **文化内涵**：融入深层的文化价值
            4. **持续创新**：保持艺术的前瞻性

            ### 艺术总结

            从艺术角度看，这个项目有潜力成为**艺术与技术完美结合的典范**，期待看到美学价值的充分体现！
                    """
        
        return result.strip()
    