# startup.py - 启动脚本
"""
启动AI Agent讨论系统的完整脚本
"""
import uvicorn
import os
import sys
from pathlib import Path

import os
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7897'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7897'

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