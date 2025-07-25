from textwrap import dedent
from pathlib import Path

from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.tools.reasoning import ReasoningTools
from agno.tools.file import FileTools
from markdown2pptx_hz import markdown2pptx

import os
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7897'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7897'
os.environ["DEEPSEEK_API_KEY"] = "sk-c3dea683f5314d0ea85e5f18a23bxxxx"

'''deepseek: sk-c3dea683f5314d0ea85e5f18a23bxxxx'''

reasoning_agent = Agent(
    model=DeepSeek(id="deepseek-chat"),
    instructions=dedent("""\
        我是一个专业的企业技术人员，我会输入一个论文网页的网址，请按照以下思路和格式总结论文，从以下几个方面：
1、生成一句话总结下这个文章的亮点。字数38个字以内。作为Markdown的一级标题。
2、文章的名称以及作者作为，一级标题下面的正文。
3、总结这个文章的摘要。300字以内，可以分点总结，要高度概括，并且通俗。Markdown格式：添加一个二级标题为"摘要"，正文是总结的内容，中间不换行。
4、总结这个文章的关键技术或创新点。300字以内，可以分点总结，要高度概括，并且通俗。Markdown格式：添加一个二级标题为"关键技术和创新点"，正文是总结的内容。
5、总结这个文章的价值和展望。300字以内，可以分点总结，要高度概括，并且通俗。Markdown格式：添加一个二级标题为"价值和展望"，正文是总结的内容。
6、总结这个文章的实验数据和效果。300字以内，可以分点总结，要高度概括，并且通俗。Markdown格式：添加一个二级标题为"实验和效果"，正文是总结的内容。
7、总结这个文章的总结小段。300字以内，可以分点总结，要高度概括，并且通俗。Markdown格式：添加一个二级标题为"总结"，正文是总结的内容。\
    """),
    tools=[
        ReasoningTools(add_instructions=True),
        FileTools(Path(".")),
    ],
    show_tool_calls=True,
    add_references=True,
    markdown=True,
)


reasoning_agent.print_response(
    "请总结 KVFlow: Efficient Prefix Caching for Accelerating LLM-Based Multi-Agent Workflows 论文，并按照我给你的格式总结，并写入文件", stream=True
)

markdown2pptx()