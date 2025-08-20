# startup.py - 启动脚本（并发优化版本）
"""
启动AI Agent讨论系统的完整脚本
使用main_optimized.py中的并发安全接口
支持多用户同时访问，数据完全隔离
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
    print("🚀 启动AI Agent讨论系统（并发优化版本）...")
    
    # 创建必要的目录
    static_dir = create_static_directory()
    
    # 检查前端文件
    index_file = static_dir / "index.html"
    if not index_file.exists():
        print("⚠️  请将前端HTML文件保存为 static/index.html")
        print("📂 前端文件路径：./static/index.html")
    
    print("✅ 系统配置检查完成")
    print("🔒 并发安全特性已启用")
    print("🌐 服务器启动地址：http://localhost:5000")
    print("📖 API文档地址：http://localhost:5000/docs")
    print("📊 支持多用户并发访问，数据完全隔离")
    
    # 启动服务器 - 使用优化后的并发安全版本
    uvicorn.run(
        "main_optimized:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()