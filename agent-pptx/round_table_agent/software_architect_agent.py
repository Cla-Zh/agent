from .agent_frm_base import AgentBase, Tool, PromptTemplate
from typing import List, Dict, Optional
from agno.tools.reasoning import ReasoningTools
from agno.tools.googlesearch import GoogleSearchTools
import asyncio
import logging

logger = logging.getLogger(__name__)

class SoftwareArchitectAgent(AgentBase):
    """软件架构师Agent - 专注于系统设计和架构规划"""

    def __init__(self):
        from .agent_frm_base import AgentConfig, AgentType
        config = AgentConfig(
            name="软件架构师",
            agent_type=AgentType.ENGINEER
        )
        super().__init__(config, "软件架构师", "软件架构师")
    
    def _setup_tools(self) -> List[Tool]:
        """设置软件架构相关工具"""
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

    async def think(self, topic: str) -> str:
        await self._simulate_thinking_time()
        logger.info(f"工程师Agent正在分析话题: {topic}")
        
        result = f"""# 工程师的观点

            ## 对"{topic}"的技术实现分析

            ### 系统架构设计

            从**技术实现**的角度，我认为需要考虑以下架构要素：

            ```
            ┌─────────────────────────────────────┐
            │            前端展示层                │
            ├─────────────────────────────────────┤
            │            业务逻辑层                │
            ├─────────────────────────────────────┤
            │            数据访问层                │
            ├─────────────────────────────────────┤
            │            基础设施层                │
            └─────────────────────────────────────┘
            ```

            ### 技术要点分析

            🔧 **核心技术栈**
            - **后端架构**：微服务架构，支持横向扩展
            - **数据库设计**：分布式数据库，保证数据一致性
            - **缓存策略**：多级缓存提升响应速度
            - **负载均衡**：动态负载分配机制

            ⚡ **性能优化**
            - **并发处理**：异步处理提升吞吐量
            - **数据压缩**：减少网络传输开销
            - **代码优化**：算法优化和代码重构
            - **监控体系**：实时性能监控和告警

            ### 技术挑战与解决方案

            | 挑战 | 解决方案 |
            |------|---------|
            | 高并发处理 | 采用异步编程模型 |
            | 数据一致性 | 分布式事务管理 |
            | 系统可用性 | 冗余设计和故障转移 |
            | 安全防护 | 多层安全防护体系 |

            ### 实施建议

            1. **敏捷开发**：采用迭代开发模式
            2. **测试驱动**：完善的单元测试和集成测试
            3. **持续集成**：自动化构建和部署
            4. **文档管理**：完整的技术文档体系

            ### 技术结论

            从工程角度看，该项目**技术可行性高**，建议采用成熟的技术栈进行实现。
        """
        
        return result.strip()
