import logging
from textwrap import dedent
from pathlib import Path
from typing import Optional, List
from markdown2pptx_hz import markdown2pptx

from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.tools.reasoning import ReasoningTools
from agno.tools.file import FileTools
from agno.tools.duckduckgo import DuckDuckGoTools

import os
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7897'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7897'
os.environ["DEEPSEEK_API_KEY"] = "sk-c3dea683f5314d0ea85e5f18a23bxxxx"

'''deepseek: sk-c3dea683f5314d0ea85e5f18a23bxxxx'''

class PaperSummarizer:
    """论文总结器 - 用于加载模板、初始化Agent并生成论文总结"""
    
    def __init__(self, 
                 model_id: str = "deepseek-chat", # 可换用其他模型
                 instructions_file: str = "dedent.md",
                 output_dir: str = ".",
                 encoding: str = "utf-8"):
        """
        初始化论文总结器
        
        Args:
            model_id: 模型ID
            instructions_file: 指令模板文件路径
            output_dir: 输出目录
            encoding: 文件编码
        """
        self.model_id = model_id
        self.instructions_file = instructions_file
        self.output_dir = Path(output_dir)
        self.encoding = encoding
        self.agent = None
        self._setup_logging()
        
    def _setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def load_instructions(self, file_path: Optional[str] = None) -> str:
        """
        从文件加载指令内容
        
        Args:
            file_path: 文件路径，如果为None则使用默认路径
            
        Returns:
            指令内容字符串
        """
        file_path = file_path or self.instructions_file
        
        try:
            content = Path(file_path).read_text(encoding=self.encoding)
            self.logger.info(f"成功加载指令文件: {file_path}")
            return content
        except FileNotFoundError:
            self.logger.warning(f"找不到文件: {file_path}")
            return ""
        except Exception as e:
            self.logger.error(f"读取文件 {file_path} 时出错: {e}")
            return ""
    
    def init_agent(self, custom_instructions: Optional[str] = None) -> bool:
        """
        初始化推理Agent
        
        Args:
            custom_instructions: 自定义指令，如果为None则从文件加载
            
        Returns:
            初始化是否成功
        """
        try:
            # 加载指令
            if custom_instructions:
                instructions = custom_instructions
            else:
                instructions = self.load_instructions()
                if not instructions:
                    self.logger.error("无法加载指令内容")
                    return False
            
            # 初始化Agent
            self.agent = Agent(
                model=DeepSeek(id=self.model_id),
                instructions=dedent(instructions),
                tools=[
                    ReasoningTools(add_instructions=True),
                    DuckDuckGoTools(),
                    FileTools(self.output_dir),
                ],
                show_tool_calls=True,
                add_references=True,
                markdown=True,
            )
            
            self.logger.info("Agent初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化Agent时出错: {e}")
            return False
    
    def summarize_paper(self, 
                       paper_title: str,
                       output_file: str = "paper_summary.md",
                       stream: bool = True) -> bool:
        """
        总结论文
        
        Args:
            paper_title: 论文标题或描述
            output_file: 输出文件名
            stream: 是否流式输出
            
        Returns:
            总结是否成功
        """
        if not self.agent:
            self.logger.error("Agent未初始化，请先调用init_agent()")
            return False
        
        try:
            prompt = f"请总结 {paper_title} 论文，并按照我给你的格式总结，并用UTF-8写入文件，文件名称为{output_file}。"
            
            self.logger.info(f"开始总结论文: {paper_title}")
            self.agent.print_response(prompt, stream=stream)
            self.logger.info(f"论文总结完成，输出文件: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"总结论文时出错: {e}")
            return False
    
    def convert_to_pptx(self, markdown_file: str = "paper_summary.md"):
        """
        将Markdown转换为PPTX
        
        Args:
            markdown_file: Markdown文件路径
        """
        try:
            self.logger.info("开始转换Markdown到PPTX")
            # 这里调用您的markdown2pptx函数
            markdown2pptx(markdown_file)
            self.logger.info("Markdown转换PPTX完成")
        except Exception as e:
            self.logger.error(f"转换PPTX时出错: {e}")
    
    def full_workflow(self, 
                     paper_title: str,
                     output_file: str = "paper_summary.md",
                     convert_pptx: bool = True) -> bool:
        """
        完整工作流：初始化 -> 总结 -> 转换
        
        Args:
            paper_title: 论文标题
            output_file: 输出文件名
            convert_pptx: 是否转换为PPTX
            
        Returns:
            工作流是否成功完成
        """
        # 初始化Agent
        if not self.init_agent():
            return False
        
        # 总结论文
        if not self.summarize_paper(paper_title, output_file):
            return False
        
        # 转换为PPTX
        if convert_pptx:
            self.convert_to_pptx(output_file)
        
        return True
    
    def batch_summarize(self, 
                       paper_list: List[str],
                       output_prefix: str = "paper_summary") -> List[str]:
        """
        批量总结论文
        
        Args:
            paper_list: 论文标题列表
            output_prefix: 输出文件前缀
            
        Returns:
            成功生成的文件列表
        """
        if not self.agent:
            if not self.init_agent():
                return []
        
        successful_files = []
        
        for i, paper_title in enumerate(paper_list, 1):
            output_file = f"{output_prefix}_{i:02d}.md"
            
            if self.summarize_paper(paper_title, output_file):
                successful_files.append(output_file)
            else:
                self.logger.warning(f"跳过论文: {paper_title}")
        
        self.logger.info(f"批量总结完成，成功生成 {len(successful_files)} 个文件")
        return successful_files


# 使用示例
def main():
    """主函数 - 使用示例"""
    
    # 方式1: 基本使用
    summarizer = PaperSummarizer()
    summarizer.full_workflow(
        "KVFlow: Efficient Prefix Caching for Accelerating LLM-Based Multi-Agent Workflows",
        "sample.md"
    )
    
    # # 方式2: 自定义配置
    # summarizer = PaperSummarizer(
    #     model_id="deepseek-chat",
    #     instructions_file="custom_template.md",
    #     output_dir="./outputs"
    # )
    
    # # 方式3: 分步执行
    # if summarizer.init_agent():
    #     summarizer.summarize_paper(
    #         "Your Paper Title Here",
    #         "custom_output.md"
    #     )
    #     summarizer.convert_to_pptx("custom_output.md")
    
    # # 方式4: 批量处理
    # papers = [
    #     "Paper 1 Title",
    #     "Paper 2 Title", 
    #     "Paper 3 Title"
    # ]
    # summarizer.batch_summarize(papers, "batch_summary")


if __name__ == "__main__":
    main()