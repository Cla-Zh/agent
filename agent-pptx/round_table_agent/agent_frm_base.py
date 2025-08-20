#!/usr/bin/env python3
"""
基于Agno框架的Agent基类和多态实现
支持不同的prompt、工具和行为模式
"""
from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.tools.reasoning import ReasoningTools
from agno.tools.file import FileTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.arxiv import ArxivTools

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
import asyncio
import logging
import random
import os
from dataclasses import dataclass
from enum import Enum
from textwrap import dedent


def read_api_key() -> str:
    """从api-key.txt文件中读取API key"""
    try:
        # 获取当前文件所在目录的上级目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        api_key_path = os.path.join(parent_dir, "api-key.txt")
        
        with open(api_key_path, 'r', encoding='utf-8') as f:
            api_key = f.read().strip()
        
        if not api_key:
            raise ValueError("API key文件为空")
        
        return api_key
    except FileNotFoundError:
        raise FileNotFoundError(f"找不到API key文件: {api_key_path}")
    except Exception as e:
        raise Exception(f"读取API key失败: {str(e)}")


class AgentType(Enum):
    """Agent类型枚举"""
    RESEARCHER = "researcher"
    CODER = "coder"
    ASSISTANT = "assistant"
    ANALYST = "analyst"
    SCIENTIST = "scientist"
    FINANCIER = "financier"
    ENGINEER = "engineer"
    LEADER = "leader"
    ENTREPRENEUR = "entrepreneur"
    ARTIST = "artist"

# 假设这些是Agno框架的核心组件
# 实际使用时需要根据Agno框架的真实API调整
# try:
#     from agno import Agent, Memory, Tool, PromptTemplate
#     from agno.tools import WebSearchTool, CodeExecutorTool, FileManagerTool
#     from agno.memory import ConversationMemory, VectorMemory
# except ImportError:
#     print("警告: Agno框架未安装，使用模拟实现")
#     # 模拟Agno框架的基础组件
#     class Agent:
#         def __init__(self, *args, **kwargs):
#             pass
    
#     class Memory:
#         def __init__(self, *args, **kwargs):
#             pass
    
class Tool:
    def __init__(self, *args, **kwargs):
        pass
    
class PromptTemplate:
    def __init__(self, template: str):
        self.template = template
 


@dataclass
class AgentConfig:
    """Agent配置类"""
    name: str
    agent_type: AgentType
    temperature: float = 0.7
    max_tokens: int = 2000
    memory_size: int = 10
    enable_tools: bool = True


class AgentBase(ABC):
    """Agent基类，定义Agent的基本框架"""
    
    def __init__(self, config: AgentConfig, name: str, role: str):
        self.config = config
        # 从文件中读取API key
        api_key = read_api_key()
        self.model = DeepSeek(id="deepseek-chat", api_key=api_key)
        self.name = config.name
        self.agent_type = config.agent_type
        self.logger = self._setup_logger()
        
        # 初始化Agno组件
        self.memory = self._setup_memory()
        self.tools = self._setup_tools()
        self.prompt_template = self._setup_prompt()
        self.agent = self._setup_agent()
        self.name = name
        self.role = role
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger(f"Agent-{self.name}")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _setup_memory(self):
        """设置记忆组件"""
        pass

    
    @abstractmethod
    def _setup_tools(self):
        """设置工具 - 子类必须实现"""
        pass
    
    @abstractmethod
    def _setup_prompt(self) -> PromptTemplate:
        """设置提示模板 - 子类必须实现"""
        pass
    
    def _setup_agent(self) -> Agent:
        """设置Agno Agent"""
        try:
            # 初始化Agent
            return Agent(
                model=self.model,
                instructions=dedent(self.prompt_template.template),
                tools=self.tools,
                show_tool_calls=True,
                add_references=True,
                markdown=True,
            )
        except Exception as e:
            self.logger.error(f"Agent初始化失败: {str(e)}")
            return Agent()
    
    async def process(self, input_text: str, context: Optional[Dict] = None) -> str:
        """处理输入并返回结果"""
        try:
            self.logger.info(f"处理输入: {input_text[:50]}...")
            
            # 预处理
            processed_input = await self._preprocess_input(input_text, context)
            
            # 使用Agno Agent处理
            result = await self._execute_agent(processed_input)
            
            # 后处理
            final_result = await self._postprocess_output(result)
            
            self.logger.info(f"处理完成")
            return final_result
            
        except Exception as e:
            self.logger.error(f"处理过程中发生错误: {str(e)}")
            return f"处理失败: {str(e)}"
    
    async def _preprocess_input(self, input_text: str, context: Optional[Dict] = None) -> str:
        """预处理输入 - 子类可重写"""
        return input_text
    
    async def _execute_agent(self, input_text: str) -> str:
        """执行Agent处理 - 使用Agno框架"""
        try:
            # 优先调用底层Agent以使用模型与工具
            if hasattr(self.agent, "run"):
                # Agno的run方法返回RunResponse对象，不是协程，所以不需要await
                response = self.agent.run(input_text)
                # 从RunResponse对象中提取内容
                if hasattr(response, 'content'):
                    return str(response.content)
                elif hasattr(response, 'text'):
                    return str(response.text)
                elif hasattr(response, 'response'):
                    return str(response.response)
                else:
                    return str(response)
            # 兜底：如无可用的Agent实现，返回简要结果
            return f"[{self.name}] 处理结果: {input_text}"
        except Exception as e:
            raise Exception(f"Agent执行失败: {str(e)}")
    
    async def _postprocess_output(self, output: str) -> str:
        """后处理输出 - 子类可重写"""
        return output
    
    def add_tool(self, tool):
        """动态添加工具"""
        if tool not in self.tools:
            self.tools.append(tool)
            self.logger.info(f"添加工具: {tool.__class__.__name__}")
    
    def remove_tool(self, tool_class: type):
        """移除工具"""
        self.tools = [tool for tool in self.tools if not isinstance(tool, tool_class)]
        self.logger.info(f"移除工具: {tool_class.__name__}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取Agent状态"""
        return {
            "name": self.name,
            "type": self.agent_type.value,
            "tools_count": len(self.tools),
            "memory_size": self.config.memory_size,
            "model": getattr(self.model, "id", str(self.model))
        }
        
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
    

# 使用示例
async def main():
    """示例使用代码"""
    
    # 这里可以导入AgentFactory来创建Agent
    # from round_table_agent.agent_factory import AgentFactory
    
    print("Agent基类定义完成")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())