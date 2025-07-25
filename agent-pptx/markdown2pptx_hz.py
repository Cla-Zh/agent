import re
from pptx import Presentation
from pptx.util import Inches, Pt, Cm
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE


def parse_markdown(file_path):
    """解析Markdown文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    slides_data = []
    current_slide = None
    
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # 一级标题 - 新幻灯片
        if line.startswith('# '):
            if current_slide:
                slides_data.append(current_slide)
            
            current_slide = {
                'title': line[2:].strip(),
                'description': '',
                'modules': []
            }
            i += 1
            
            # 收集描述文字（一级标题后到二级标题前的内容）
            description_lines = []
            while i < len(lines):
                if lines[i].strip().startswith('## '):
                    break
                if lines[i].strip():
                    description_lines.append(lines[i].strip())
                i += 1
            
            current_slide['description'] = ' '.join(description_lines)
            continue
            
        # 二级标题 - 模块标题
        elif line.startswith('## '):
            if current_slide:
                module_title = line[3:].strip()
                module_content = []
                i += 1
                
                # 收集该模块的内容（直到下一个二级标题或一级标题）
                while i < len(lines):
                    next_line = lines[i].strip()
                    if next_line.startswith('# ') or next_line.startswith('## '):
                        break
                    if next_line:
                        module_content.append(next_line)
                    i += 1
                
                current_slide['modules'].append({
                    'title': module_title,
                    'content': ' '.join(module_content)
                })
                continue
        
        i += 1
    
    # 添加最后一个幻灯片
    if current_slide:
        slides_data.append(current_slide)
    
    return slides_data


def apply_text_formatting(text_frame, text_content):
    """应用文本格式，处理粗体标记，保持换行结构"""
    # 清空现有内容
    text_frame.clear()
    
    # 按行分割文本内容
    lines = text_content.split('\n')
    
    for line_idx, line in enumerate(lines):
        line = line.strip()
        if not line:  # 跳过空行，但保持段落分隔
            if line_idx < len(lines) - 1:  # 不是最后一行
                text_frame.add_paragraph()
            continue
            
        # 为每一行创建段落（第一行使用默认段落）
        if line_idx == 0:
            p = text_frame.paragraphs[0]
        else:
            p = text_frame.add_paragraph()
        
        # 使用正则表达式分割该行文本，保留**标记
        parts = re.split(r'(\*\*.*?\*\*)', line)
        
        # 在同一段落中处理加粗和普通文字
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                # 粗体文本 - 在同一行内，不换行
                run = p.add_run()
                run.text = part[2:-2]  # 去掉**标记
                run.font.bold = True
            else:
                # 普通文本
                if part:  # 非空字符串
                    run = p.add_run()
                    run.text = part


def calculate_text_height(text, width_cm, font_size, line_spacing=1.0):
    """估算文本高度（厘米）"""
    # 简单估算：假设每行大约能容纳的字符数
    chars_per_line = int(width_cm * 10 / (font_size * 0.6))  # 粗略估算
    lines = len(text) // chars_per_line + 1
    
    # 每行高度约为字号的1.2倍（点数转厘米）
    line_height_cm = font_size * 0.035 * line_spacing  # 1点 ≈ 0.035厘米
    return lines * line_height_cm


def create_pptx_from_markdown(markdown_file, output_file):
    """从Markdown创建PPTX"""
    # 解析Markdown
    slides_data = parse_markdown(markdown_file)
    
    # 创建演示文稿
    prs = Presentation()
    
    # 设置幻灯片尺寸为16:9
    prs.slide_width = Inches(13.33)  # 16:9比例
    prs.slide_height = Inches(7.5)
    
    for slide_data in slides_data:
        # 创建空白幻灯片
        slide_layout = prs.slide_layouts[6]  # 空白布局
        slide = prs.slides.add_slide(slide_layout)
        
        # 1. 顶层主标题
        title_left = Cm(0)
        title_top = Cm(0)
        title_width = Cm(30)
        title_height = Cm(1.5)
        
        title_shape = slide.shapes.add_textbox(title_left, title_top, title_width, title_height)
        title_frame = title_shape.text_frame
        title_frame.text = slide_data['title']
        title_frame.paragraphs[0].alignment = PP_ALIGN.LEFT
        title_frame.paragraphs[0].font.name = '微软雅黑'
        title_frame.paragraphs[0].font.size = Pt(18)
        title_frame.paragraphs[0].font.color.rgb = RGBColor(139, 0, 0)  # 深红色
        
        # 2. 中层矩形解释框
        desc_left = Cm(0)
        desc_top = Cm(1.7)
        desc_width = Cm(34)
        desc_height = Cm(0.6)
        
        desc_shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, desc_left, desc_top, desc_width, desc_height
        )
        desc_shape.fill.solid()
        desc_shape.fill.fore_color.rgb = RGBColor(139, 0, 0)  # 深红色背景
        desc_shape.line.fill.background()  # 无边框
        desc_shape.shadow.inherit = False  # 无阴影
        
        desc_frame = desc_shape.text_frame
        desc_frame.text = slide_data['description']
        desc_frame.paragraphs[0].alignment = PP_ALIGN.LEFT
        desc_frame.paragraphs[0].font.name = '微软雅黑'
        desc_frame.paragraphs[0].font.size = Pt(6)
        desc_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)  # 白色文字
        
        # 3. 底层模块
        modules = slide_data['modules']
        left_modules = modules[:3]  # 左边3个
        right_modules = modules[3:5]  # 右边2个
        
        # 左边模块
        current_y = 3.0  # 起始垂直位置（厘米）
        for i, module in enumerate(left_modules):
            # 标题矩形
            title_left = Cm(1)
            title_top = Cm(current_y)
            title_width = Cm(6)
            title_height = Cm(0.8)
            
            title_shape = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, title_left, title_top, title_width, title_height
            )
            title_shape.fill.solid()
            title_shape.fill.fore_color.rgb = RGBColor(139, 0, 0)  # 深红色背景
            title_shape.line.fill.background()  # 无边框
            title_shape.shadow.inherit = False  # 无阴影
            
            title_frame = title_shape.text_frame
            title_frame.text = module['title']
            title_frame.paragraphs[0].alignment = PP_ALIGN.LEFT
            title_frame.paragraphs[0].font.name = '微软雅黑'
            title_frame.paragraphs[0].font.size = Pt(14)
            title_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)  # 白色文字
            
            # 内容文本框
            content_left = Cm(1)
            content_top = Cm(current_y + 0.8)
            content_width = Cm(14.5)
            content_height = Cm(4)
            
            content_shape = slide.shapes.add_textbox(content_left, content_top, content_width, content_height)
            content_shape.shadow.inherit = False  # 无阴影
            content_frame = content_shape.text_frame
            content_frame.word_wrap = True
            
            # 应用格式化文本
            apply_text_formatting(content_frame, module['content'])
            
            # 设置字体
            for paragraph in content_frame.paragraphs:
                paragraph.alignment = PP_ALIGN.LEFT
                for run in paragraph.runs:
                    run.font.name = '微软雅黑'
                    run.font.size = Pt(10)
            
            # 计算下一个模块的位置
            text_height = calculate_text_height(module['content'], 14.5, 10)
            module_total_height = max(4.0, text_height + 0.8)  # 标题高度0.8cm
            current_y += module_total_height + 0.5  # 模块间距0.5cm
        
        # 右边模块
        current_y = 3.0  # 重置起始位置
        for i, module in enumerate(right_modules):
            # 标题矩形
            title_left = Cm(16)
            title_top = Cm(current_y)
            title_width = Cm(6)
            title_height = Cm(0.8)
            
            title_shape = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, title_left, title_top, title_width, title_height
            )
            title_shape.fill.solid()
            title_shape.fill.fore_color.rgb = RGBColor(139, 0, 0)  # 深红色背景
            title_shape.line.fill.background()  # 无边框
            title_shape.shadow.inherit = False  # 无阴影
            
            title_frame = title_shape.text_frame
            title_frame.text = module['title']
            title_frame.paragraphs[0].alignment = PP_ALIGN.LEFT
            title_frame.paragraphs[0].font.name = '微软雅黑'
            title_frame.paragraphs[0].font.size = Pt(14)
            title_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)  # 白色文字
            
            # 内容文本框
            content_left = Cm(16)
            content_top = Cm(current_y + 0.8)
            content_width = Cm(14.5)
            content_height = Cm(6)
            
            content_shape = slide.shapes.add_textbox(content_left, content_top, content_width, content_height)
            content_shape.shadow.inherit = False  # 无阴影
            content_frame = content_shape.text_frame
            content_frame.word_wrap = True
            
            # 应用格式化文本
            apply_text_formatting(content_frame, module['content'])
            
            # 设置字体
            for paragraph in content_frame.paragraphs:
                paragraph.alignment = PP_ALIGN.LEFT
                for run in paragraph.runs:
                    run.font.name = '微软雅黑'
                    run.font.size = Pt(10)
            
            # 计算下一个模块的位置
            text_height = calculate_text_height(module['content'], 14.5, 10)
            module_total_height = max(6.0, text_height + 0.8)  # 标题高度0.8cm
            current_y += module_total_height + 0.5  # 模块间距0.5cm
    
    # 保存文件
    prs.save(output_file)
    print(f"PPT已生成：{output_file}")


def main():
    """主函数"""
    markdown_file = "sample.md"
    output_file = "output.pptx"
    
    try:
        create_pptx_from_markdown(markdown_file, output_file)
    except FileNotFoundError:
        print(f"错误：找不到文件 {markdown_file}")
        print("请确保在当前目录下存在 sample.md 文件")
    except Exception as e:
        print(f"转换过程中出现错误：{e}")


if __name__ == "__main__":
    main()