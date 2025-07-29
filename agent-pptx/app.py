import os
import json
import logging
import threading
import queue
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable
from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS

# 导入原有的PaperSummarizer类
from agent_agno_framework import PaperSummarizer

class WebLogHandler(logging.Handler):
    """自定义日志处理器，用于将日志发送到Web界面"""
    
    def __init__(self):
        super().__init__()
        self.log_queue = queue.Queue()
    
    def emit(self, record):
        """发送日志记录"""
        try:
            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created).strftime('%H:%M:%S'),
                'level': record.levelname.lower(),
                'message': self.format(record)
            }
            
            # 添加到队列
            self.log_queue.put(log_entry)
                
        except Exception:
            self.handleError(record)
    
    def get_logs(self):
        """获取所有日志"""
        logs = []
        while not self.log_queue.empty():
            try:
                logs.append(self.log_queue.get_nowait())
            except queue.Empty:
                break
        return logs

class WebPaperSummarizer:
    """Web版论文总结器包装类"""
    
    def __init__(self, output_dir: str = "."):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.summarizer = None
        self.web_log_handler = None
        self.progress_callback = None
        self.task_logs = []
        self._setup_web_logging()
    
    def _setup_web_logging(self):
        """设置Web日志处理"""
        self.web_log_handler = WebLogHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.web_log_handler.setFormatter(formatter)
        
        # 获取根日志记录器并添加我们的处理器
        root_logger = logging.getLogger()
        root_logger.addHandler(self.web_log_handler)
        root_logger.setLevel(logging.INFO)
    
    def set_progress_callback(self, callback: Callable):
        """设置进度回调函数"""
        self.progress_callback = callback
    
    def _update_progress(self, percent: int, message: str = ""):
        """更新进度"""
        if self.progress_callback:
            self.progress_callback(percent, message)
    
    def get_web_logs(self):
        """获取Web日志"""
        if self.web_log_handler:
            new_logs = self.web_log_handler.get_logs()
            self.task_logs.extend(new_logs)
            return new_logs
        return []
    
    def clear_logs(self):
        """清空日志"""
        self.task_logs = []
        # 清空队列
        if self.web_log_handler:
            while not self.web_log_handler.log_queue.empty():
                try:
                    self.web_log_handler.log_queue.get_nowait()
                except queue.Empty:
                    break
    
    def run_workflow(self, paper_title: str, output_file: str = "paper_summary.md") -> bool:
        """运行完整工作流，带进度回调"""
        try:
            self._update_progress(5, "准备开始...")
            
            # 创建新的PaperSummarizer实例
            self.summarizer = PaperSummarizer(
                output_dir=str(self.output_dir)
            )
            
            self._update_progress(10, "正在初始化智能体...")
            
            # 初始化Agent
            if not self.summarizer.init_agent():
                return False
            
            self._update_progress(40, "正在分析论文内容...")
            
            # 总结论文
            if not self.summarizer.summarize_paper(paper_title, output_file):
                return False
            
            self._update_progress(80, "正在转换为PPT格式...")
            
            # 转换为PPTX
            self.summarizer.convert_to_pptx(output_file)
            
            self._update_progress(100, "生成完成！")
            return True
            
        except Exception as e:
            logging.error(f"工作流执行出错: {e}")
            return False
    
    def get_output_files(self):
        """获取输出目录中的文件列表"""
        files = {
            'markdown': [],
            'pptx': []
        }
        
        if self.output_dir.exists():
            for file_path in self.output_dir.iterdir():
                if file_path.is_file():
                    if file_path.suffix == '.md':
                        files['markdown'].append(file_path.name)
                    elif file_path.suffix == '.pptx':
                        files['pptx'].append(file_path.name)
        
        return files

# Flask应用设置
app = Flask(__name__)
CORS(app)

# 全局变量
current_summarizer = None
current_task_status = {
    'is_running': False,
    'progress': 0,
    'message': '',
    'success': False,
    'logs': []
}

def progress_callback(percent: int, message: str = ""):
    """进度回调函数"""
    global current_task_status
    current_task_status['progress'] = percent
    current_task_status['message'] = message

@app.route('/')
def index():
    """主页 - 返回HTML界面"""
    html_content = Path("index.html").read_text("utf-8")
    
    return render_template_string(html_content)

@app.route('/api/summarize', methods=['POST'])
def api_summarize():
    """论文总结API"""
    global current_summarizer, current_task_status
    
    try:
        data = request.get_json()
        paper_title = data.get('paper_title', '').strip()
        output_file = data.get('output_file', 'paper_summary.md')
        
        if not paper_title:
            return jsonify({'success': False, 'error': '请输入论文标题'}), 400
        
        if current_task_status['is_running']:
            return jsonify({'success': False, 'error': '已有任务正在执行中'}), 400
        
        # 重置状态
        current_task_status = {
            'is_running': True,
            'progress': 0,
            'message': '准备开始...',
            'success': False,
            'logs': []
        }
        
        # 创建新的总结器实例
        current_summarizer = WebPaperSummarizer()
        current_summarizer.set_progress_callback(progress_callback)
        current_summarizer.clear_logs()
        
        # 在后台线程执行任务
        def run_task():
            print("------------run task----------------")
            global current_task_status
            try:
                success = current_summarizer.run_workflow(paper_title, output_file)
                current_task_status['is_running'] = False
                current_task_status['success'] = success
                
                if success:
                    current_task_status['message'] = '生成完成！'
                    current_task_status['progress'] = 100
                else:
                    current_task_status['message'] = '生成失败'
                    
            except Exception as e:
                current_task_status['is_running'] = False
                current_task_status['success'] = False
                current_task_status['message'] = f'执行出错: {str(e)}'
        
        thread = threading.Thread(target=run_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'message': '任务已开始执行'})
        
    except Exception as e:
        current_task_status['is_running'] = False
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    """获取任务状态"""
    global current_task_status, current_summarizer
    
    # 获取最新日志
    new_logs = []
    if current_summarizer:
        new_logs = current_summarizer.get_web_logs()
    
    # 构建响应
    response = {
        'is_running': current_task_status['is_running'],
        'progress': current_task_status['progress'],
        'message': current_task_status['message'],
        'success': current_task_status.get('success', False),
        'logs': new_logs
    }
    
    return jsonify(response)

@app.route('/api/download/<filename>', methods=['GET'])
def api_download(filename):
    """文件下载API"""
    global current_summarizer
    
    if not current_summarizer:
        return jsonify({'error': '无可用的总结器实例'}), 404
    
    try:
        file_path = current_summarizer.output_dir / filename
        
        if not file_path.exists():
            return jsonify({'error': '文件不存在'}), 404
        
        return send_file(
            str(file_path),
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files', methods=['GET'])
def api_files():
    """获取输出文件列表"""
    global current_summarizer
    
    if not current_summarizer:
        return jsonify({'files': {'markdown': [], 'pptx': []}})
    
    try:
        files = current_summarizer.get_output_files()
        return jsonify({'files': files})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_web_server(host='127.0.0.1', port=5000, debug=False):
    """运行Web服务器"""
    print(f"🚀 启动Web服务器: http://{host}:{port}")
    print("📝 在浏览器中打开上述地址即可使用论文总结智能体")
    app.run(host=host, port=port, debug=debug, threaded=True)

if __name__ == "__main__":
    run_web_server(debug=True)