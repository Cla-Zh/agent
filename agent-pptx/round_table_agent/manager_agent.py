from .agent_frm_base import AgentBase, Tool, PromptTemplate
from typing import List, Dict, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)

class ManagerAgent(AgentBase):
    """管理者Agent - 专注于项目管理和团队协调"""

    def __init__(self):
        from .agent_frm_base import AgentConfig, AgentType
        config = AgentConfig(
            name="领导者",
            agent_type=AgentType.LEADER
        )
        super().__init__(config, "领导者", "领导者")
    
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

    async def think(self, topic: str) -> str:
        await self._simulate_thinking_time()
        logger.info(f"领导Agent正在分析话题: {topic}")
        
        result = f"""# 领导的观点

            ## 对"{topic}"的战略管理思考

            ### 战略规划框架

            作为**团队领导者**，我从管理和战略的角度提出以下观点：

            🎯 **愿景与使命**
            - **长期愿景**：3-5年发展目标
            - **核心使命**：价值创造和社会责任
            - **战略定位**：行业领先地位

            📋 **SWOT分析**

            | 优势(Strengths) | 劣势(Weaknesses) |
            |----------------|------------------|
            | 团队专业能力强 | 资源相对有限 |
            | 创新能力突出 | 市场经验不足 |

            | 机会(Opportunities) | 威胁(化氛围

            📊 **项目管理**
            - **目标设定**：SMART原则制定目标
            - **资源配置**：优化资源分配效率
            - **风险管控**：建立风险预警机制
            - **质量保证**：严格的质量管理体系

            ### 执行路线图

            ```mermaid
            graph LR
                A[策略制定] --> B[资源整合]
                B --> C[团队组建]
                C --> D[项目启动]
                D --> E[执行监控]
                E --> F[评估调整]
            ```

            ### 管理建议

            1. **建立跨部门协作机制**
            2. **制定详细的里程碑计划**
            3. **建立有效的沟通渠道**
            4. **培养团队的执行能力**

            ### 领导总结

            从管理角度看，成功的关键在于**战略清晰、执行有力、团队协作**。Threats) |
            |-------------------|---------------|
            | 市场需求增长 | 竞争日趋激烈 |
            | 政策支持利好 | 技术变化快速 |

            ### 组织管理策略

            👥 **团队建设**
            - **人才招募**：吸引顶尖人才加入
            - **能力培养**：持续的培训和发展
            - **激励机制**：完善的绩效考核体系
            - **文化建设**：营造创新协作的文
        """
        
        return result.strip()
