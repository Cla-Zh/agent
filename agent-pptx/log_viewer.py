#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志查看工具 - 用于查看多用户并发的日志
"""

import os
import glob
import re
from datetime import datetime
from pathlib import Path

def list_session_logs():
    """列出所有会话日志文件"""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print("❌ logs目录不存在")
        return []
    
    log_files = list(logs_dir.glob("session_*.log"))
    log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    print(f"📁 找到 {len(log_files)} 个会话日志文件:")
    print("-" * 60)
    
    for i, log_file in enumerate(log_files, 1):
        stat = log_file.stat()
        size = stat.st_size
        mtime = datetime.fromtimestamp(stat.st_mtime)
        
        # 提取会话ID
        session_id = log_file.stem.replace("session_", "")
        
        print(f"{i:2d}. {log_file.name}")
        print(f"    会话ID: {session_id}")
        print(f"    大小: {size:,} 字节")
        print(f"    修改时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    return log_files

def view_session_log(session_id: str = None, log_file_path: str = None):
    """查看指定会话的日志"""
    if log_file_path:
        log_file = Path(log_file_path)
    elif session_id:
        log_file = Path(f"logs/session_{session_id}.log")
    else:
        print("❌ 请指定会话ID或日志文件路径")
        return
    
    if not log_file.exists():
        print(f"❌ 日志文件不存在: {log_file}")
        return
    
    print(f"📖 查看日志文件: {log_file.name}")
    print("=" * 80)
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            print("📄 日志文件为空")
            return
        
        # 按行显示日志
        lines = content.strip().split('\n')
        for i, line in enumerate(lines, 1):
            print(f"{i:4d}: {line}")
            
    except Exception as e:
        print(f"❌ 读取日志文件失败: {e}")

def search_logs(keyword: str, session_id: str = None):
    """在日志中搜索关键词"""
    if session_id:
        log_files = [Path(f"logs/session_{session_id}.log")]
    else:
        log_files = list(Path("logs").glob("session_*.log"))
    
    print(f"🔍 搜索关键词: '{keyword}'")
    print("=" * 80)
    
    found_count = 0
    for log_file in log_files:
        if not log_file.exists():
            continue
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            file_found = False
            
            for i, line in enumerate(lines, 1):
                if keyword.lower() in line.lower():
                    if not file_found:
                        print(f"\n📁 文件: {log_file.name}")
                        file_found = True
                    
                    print(f"  {i:4d}: {line}")
                    found_count += 1
                    
        except Exception as e:
            print(f"❌ 读取文件失败 {log_file}: {e}")
    
    print(f"\n✅ 搜索完成，找到 {found_count} 条匹配记录")

def show_recent_activity(minutes: int = 30):
    """显示最近的活动"""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print("❌ logs目录不存在")
        return
    
    cutoff_time = datetime.now().timestamp() - (minutes * 60)
    log_files = list(logs_dir.glob("session_*.log"))
    
    print(f"🕒 最近 {minutes} 分钟的活动:")
    print("=" * 80)
    
    recent_activities = []
    
    for log_file in log_files:
        stat = log_file.stat()
        if stat.st_mtime >= cutoff_time:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 获取最后几行
                last_lines = lines[-5:] if len(lines) > 5 else lines
                
                session_id = log_file.stem.replace("session_", "")
                recent_activities.append({
                    'session_id': session_id,
                    'file': log_file,
                    'last_lines': last_lines,
                    'mtime': stat.st_mtime
                })
                
            except Exception as e:
                print(f"❌ 读取文件失败 {log_file}: {e}")
    
    # 按时间排序
    recent_activities.sort(key=lambda x: x['mtime'], reverse=True)
    
    for activity in recent_activities:
        mtime = datetime.fromtimestamp(activity['mtime'])
        print(f"\n📁 会话: {activity['session_id']} (最后更新: {mtime.strftime('%H:%M:%S')})")
        print("-" * 60)
        
        for line in activity['last_lines']:
            line = line.strip()
            if line:
                print(f"  {line}")
    
    if not recent_activities:
        print("📭 没有找到最近的活动")

def main():
    """主菜单"""
    while True:
        print("\n" + "=" * 60)
        print("📊 AI Agent讨论系统 - 日志查看工具")
        print("=" * 60)
        print("1. 列出所有会话日志")
        print("2. 查看指定会话日志")
        print("3. 搜索日志内容")
        print("4. 显示最近活动")
        print("5. 退出")
        print("-" * 60)
        
        choice = input("请选择操作 (1-5): ").strip()
        
        if choice == "1":
            list_session_logs()
            
        elif choice == "2":
            session_id = input("请输入会话ID: ").strip()
            if session_id:
                view_session_log(session_id=session_id)
            else:
                print("❌ 请输入有效的会话ID")
                
        elif choice == "3":
            keyword = input("请输入搜索关键词: ").strip()
            if keyword:
                session_id = input("请输入会话ID (可选，直接回车搜索所有): ").strip()
                search_logs(keyword, session_id if session_id else None)
            else:
                print("❌ 请输入搜索关键词")
                
        elif choice == "4":
            try:
                minutes = int(input("请输入时间范围(分钟，默认30): ").strip() or "30")
                show_recent_activity(minutes)
            except ValueError:
                print("❌ 请输入有效的数字")
                
        elif choice == "5":
            print("👋 再见!")
            break
            
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == "__main__":
    main()
