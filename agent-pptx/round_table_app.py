# main.py - FastAPI主服务器
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
import uuid
from typing import Dict, List
import json
from datetime import datetime
import logging

from agents import AgentManager
from models import DiscussionRequest, DiscussionResponse, AgentResult

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Agent Discussion System", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务（用于前端页面）
app.mount("/static", StaticFiles(directory="static"), name="static")

# 全局Agent管理器
agent_manager = AgentManager()

# 存储讨论会话
discussions: Dict[str, Dict] = {}

@app.get("/")
async def read_index():
    """提供前端页面"""
    from fastapi.responses import FileResponse
    return FileResponse('static/index.html')

@app.post("/api/discuss", response_model=DiscussionResponse)
async def start_discussion(request: DiscussionRequest):
    """
    开始AI Agent讨论
    """
    try:
        # 生成会话ID
        session_id = str(uuid.uuid4())
        
        # 初始化讨论会话
        discussions[session_id] = {
            "topic": request.topic,
            "status": "processing",
            "created_at": datetime.now(),
            "results": {},
            "completed_agents": []
        }
        
        logger.info(f"开始新讨论会话: {session_id}, 话题: {request.topic}")
        
        # 启动异步思考任务
        asyncio.create_task(process_discussion(session_id, request.topic))
        
        return DiscussionResponse(
            session_id=session_id,
            status="started",
            message="讨论已开始，各Agent正在思考中..."
        )
        
    except Exception as e:
        logger.error(f"启动讨论失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动讨论失败: {str(e)}")

@app.get("/api/discuss/{session_id}/status")
async def get_discussion_status(session_id: str):
    """
    获取讨论状态和结果
    """
    if session_id not in discussions:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    discussion = discussions[session_id]
    
    return {
        "session_id": session_id,
        "status": discussion["status"],
        "topic": discussion["topic"],
        "results": discussion["results"],
        "completed_agents": discussion["completed_agents"],
        "total_agents": len(agent_manager.get_all_agents()),
        "progress": len(discussion["completed_agents"]) / len(agent_manager.get_all_agents())
    }

@app.get("/api/discuss/{session_id}/result/{agent_key}")
async def get_agent_result(session_id: str, agent_key: str):
    """
    获取特定Agent的思考结果
    """
    if session_id not in discussions:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    discussion = discussions[session_id]
    
    if agent_key not in discussion["results"]:
        raise HTTPException(status_code=404, detail="该Agent尚未完成思考")
    
    return discussion["results"][agent_key]

async def process_discussion(session_id: str, topic: str):
    """
    异步处理讨论 - 多Agent并发思考
    """
    try:
        logger.info(f"开始处理讨论 {session_id}: {topic}")
        
        # 获取所有Agent
        agents = agent_manager.get_all_agents()
        
        # 创建异步任务列表
        tasks = []
        for agent_key, agent in agents.items():
            task = asyncio.create_task(
                run_agent_thinking(session_id, agent_key, agent, topic)
            )
            tasks.append(task)
        
        # 等待所有Agent完成思考
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                agent_key = list(agents.keys())[i]
                logger.error(f"Agent {agent_key} 执行异常: {result}")
        
        # 更新讨论状态为完成
        discussions[session_id]["status"] = "completed"
        logger.info(f"讨论 {session_id} 已完成")
        
    except Exception as e:
        logger.error(f"讨论处理错误: {e}")
        discussions[session_id]["status"] = "error"

async def run_agent_thinking(session_id: str, agent_key: str, agent, topic: str):
    """
    运行单个Agent的思考过程
    """
    try:
        logger.info(f"Agent {agent_key} 开始思考话题: {topic}")
        
        # 调用Agent的思考方法
        result = await agent.think(topic)
        
        # 保存结果
        discussions[session_id]["results"][agent_key] = {
            "agent_key": agent_key,
            "agent_name": agent.role,
            "content": result,
            "status": "completed",
            "completed_at": datetime.now().isoformat()
        }
        
        # 添加到已完成列表
        discussions[session_id]["completed_agents"].append(agent_key)
        
        logger.info(f"Agent {agent_key} 思考完成")
        
    except Exception as e:
        logger.error(f"Agent {agent_key} 思考错误: {e}")
        discussions[session_id]["results"][agent_key] = {
            "agent_key": agent_key,
            "agent_name": getattr(agent, 'role', agent_key),
            "content": f"思考过程中出现错误: {str(e)}",
            "status": "error",
            "completed_at": datetime.now().isoformat()
        }
        discussions[session_id]["completed_agents"].append(agent_key)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


# models.py - 数据模型定义
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

class DiscussionRequest(BaseModel):
    """讨论请求模型"""
    topic: str = Field(..., min_length=1, max_length=60, description="讨论话题，最多60字")
    
    class Config:
        schema_extra = {
            "example": {
                "topic": "人工智能对未来教育的影响"
            }
        }

class DiscussionResponse(BaseModel):
    """讨论响应模型"""
    session_id: str
    status: str  # started, processing, completed, error
    message: str

class AgentResult(BaseModel):
    """Agent思考结果模型"""
    agent_key: str
    agent_name: str
    content: str
    status: str  # completed, error
    completed_at: str

class AgentStatus(BaseModel):
    """Agent状态模型"""
    agent_key: str
    agent_name: str
    status: str  # thinking, completed, error
    has_result: bool


# agents.py - Agent管理器和具体Agent实现
import asyncio
import random
from abc import ABC, abstractmethod
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
    
    @abstractmethod
    async def think(self, topic: str) -> str:
        """
        Agent思考方法 - 子类必须实现
        返回markdown格式的思考结果
        """
        pass
    
    async def _simulate_thinking_time(self):
        """模拟思考时间"""
        # 随机2-8秒的思考时间，模拟真实的AI处理时间
        thinking_time = random.uniform(2, 8)
        await asyncio.sleep(thinking_time)

class ScientistAgent(BaseAgent):
    """科学家Agent"""
    
    def __init__(self):
        super().__init__("scientist", "科学家")
    
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

class FinancierAgent(BaseAgent):
    """金融家Agent"""
    
    def __init__(self):
        super().__init__("financier", "金融家")
    
    async def think(self, topic: str) -> str:
        await self._simulate_thinking_time()
        logger.info(f"金融家Agent正在分析话题: {topic}")
        
        result = f"""# 金融家的观点

## 对"{topic}"的投资与财务分析

### 市场机会评估
从**投资和资本市场**的视角分析，我看到以下机会：

💰 **投资价值**
- 市场规模潜力巨大
- 具备长期增长动力
- 符合未来发展趋势

📈 **商业模式分析**
- **收入模式**：多元化收入来源
- **成本结构**：可控的运营成本
- **盈利能力**：良好的利润率预期

### 风险评估矩阵

| 风险类型 | 概率 | 影响度 | 应对策略 |
|---------|------|--------|---------|
| 市场风险 | 中等 | 高 | 分散投资组合 |
| 政策风险 | 低 | 中 | 密切关注政策变化 |
| 技术风险 | 中等 | 中 | 技术储备与创新 |
| 竞争风险 | 高 | 高 | 建立护城河 |

### 财务建议

1. **资金配置**：建议采用阶段性投资策略
2. **现金流管理**：确保充足的运营资金
3. **风险对冲**：建立完善的风险管理体系
4. **退出机制**：制定清晰的退出策略

### 投资结论

从财务角度看，这是一个**值得关注的投资机会**，建议进行深度尽职调查后考虑投资。
        """
        
        return result.strip()

class EngineerAgent(BaseAgent):
    """工程师Agent"""
    
    def __init__(self):
        super().__init__("engineer", "工程师")
    
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

class LeaderAgent(BaseAgent):
    """领导Agent"""
    
    def __init__(self):
        super().__init__("leader", "领导")
    
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

| 机会(Opportunities) | 威胁(Threats) |
|-------------------|---------------|
| 市场需求增长 | 竞争日趋激烈 |
| 政策支持利好 | 技术变化快速 |

### 组织管理策略

👥 **团队建设**
- **人才招募**：吸引顶尖人才加入
- **能力培养**：持续的培训和发展
- **激励机制**：完善的绩效考核体系
- **文化建设**：营造创新协作的文化氛围

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

从管理角度看，成功的关键在于**战略清晰、执行有力、团队协作**。
        """
        
        return result.strip()

class EntrepreneurAgent(BaseAgent):
    """企业家Agent"""
    
    def __init__(self):
        super().__init__("entrepreneur", "企业家")
    
    async def think(self, topic: str) -> str:
        await self._simulate_thinking_time()
        logger.info(f"企业家Agent正在分析话题: {topic}")
        
        result = f"""# 企业家的观点

## 对"{topic}"的创业商业洞察

### 商业机会识别

从**创业者和商业创新**的角度，我发现了巨大的商业潜力：

🚀 **市场洞察**
- **用户痛点**：深度挖掘未被满足的需求
- **市场空白**：识别蓝海市场机会
- **趋势把握**：紧跟行业发展趋势
- **需求验证**：快速验证市场需求

💡 **创新商业模式**

```
价值主张画布：
┌─────────────────┬─────────────────┐
│   价值创造      │   客户细分      │
│ • 解决核心痛点  │ • 目标用户群体  │
│ • 提升用户体验  │ • 用户行为特征  │
│ • 降低使用成本  │ • 付费意愿分析  │
└─────────────────┴─────────────────┘
```

### 创业策略

🎯 **产品策略**
- **MVP开发**：最小可行产品快速上市
- **迭代优化**：基于用户反馈持续改进
- **功能扩展**：逐步完善产品功能
- **用户体验**：打造极致的用户体验

📈 **增长策略**
- **获客模式**：多渠道获客策略
- **用户留存**：提升用户粘性和活跃度
- **病毒传播**：设计传播机制
- **数据驱动**：基于数据优化运营

### 竞争优势构建

| 优势类型 | 具体策略 | 预期效果 |
|---------|---------|---------|
| 产品优势 | 技术创新 | 功能领先 |
| 运营优势 | 效率提升 | 成本控制 |
| 品牌优势 | 口碑营销 | 用户信任 |
| 渠道优势 | 合作伙伴 | 市场覆盖 |

### 融资与扩张

💰 **资金策略**
- **天使轮**：验证商业模式
- **A轮**：扩大市场份额
- **B轮及以后**：规模化扩张

🌍 **扩张路径**
1. 本地市场深耕
2. 区域市场拓展
3. 全国市场布局
4. 国际市场进入

### 创业结论

这个领域具有**巨大的创业机会**，建议快速行动，抢占市场先机！
        """
        
        return result.strip()

class ArtistAgent(BaseAgent):
    """艺术家Agent"""
    
    def __init__(self):
        super().__init__("artist", "艺术家")
    
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

class AgentManager:
    """Agent管理器"""
    
    def __init__(self):
        self.agents = {
            "scientist": ScientistAgent(),
            "financier": FinancierAgent(), 
            "engineer": EngineerAgent(),
            "leader": LeaderAgent(),
            "entrepreneur": EntrepreneurAgent(),
            "artist": ArtistAgent()
        }
        logger.info(f"初始化完成，共加载 {len(self.agents)} 个Agent")
    
    def get_all_agents(self) -> Dict[str, BaseAgent]:
        """获取所有Agent"""
        return self.agents
    
    def get_agent(self, agent_key: str) -> BaseAgent:
        """获取特定Agent"""
        return self.agents.get(agent_key)
    
    def get_agent_keys(self) -> List[str]:
        """获取所有Agent的键"""
        return list(self.agents.keys())
    
    async def run_all_agents(self, topic: str) -> Dict[str, str]:
        """并发运行所有Agent（测试用）"""
        tasks = []
        for agent_key, agent in self.agents.items():
            task = asyncio.create_task(agent.think(topic))
            tasks.append((agent_key, task))
        
        results = {}
        for agent_key, task in tasks:
            try:
                result = await task
                results[agent_key] = result
            except Exception as e:
                logger.error(f"Agent {agent_key} 执行失败: {e}")
                results[agent_key] = f"思考过程中出现错误: {str(e)}"
        
        return results


# config.py - 配置文件
import os
from typing import Optional

class Settings:
    """应用配置"""
    
    # 服务器配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Agent配置
    AGENT_THINKING_TIME_MIN: float = float(os.getenv("THINKING_TIME_MIN", "2.0"))
    AGENT_THINKING_TIME_MAX: float = float(os.getenv("THINKING_TIME_MAX", "8.0"))
    
    # 会话管理
    SESSION_EXPIRE_HOURS: int = int(os.getenv("SESSION_EXPIRE_HOURS", "24"))
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()


# requirements.txt
"""
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
aiofiles==23.2.1
"""


# startup.py - 启动脚本
"""
启动AI Agent讨论系统的完整脚本
"""
import uvicorn
import os
import sys
from pathlib import Path

def create_static_directory():
    """创建静态文件目录"""
    static_dir = Path("static")
    if not static_dir.exists():
        static_dir.mkdir()
        print("✅ 创建static目录")
    return static_dir

def main():
    """主启动函数"""
    print("🚀 启动AI Agent讨论系统...")
    
    # 创建必要的目录
    static_dir = create_static_directory()
    
    # 检查前端文件
    index_file = static_dir / "index.html"
    if not index_file.exists():
        print("⚠️  请将前端HTML文件保存为 static/index.html")
        print("📂 前端文件路径：./static/index.html")
    
    print("✅ 系统配置检查完成")
    print("🌐 服务器启动地址：http://localhost:8000")
    print("📖 API文档地址：http://localhost:8000/docs")
    
    # 启动服务器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()