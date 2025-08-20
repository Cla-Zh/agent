#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多用户并发时的日志隔离功能
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

async def simulate_user_session(user_id: int, topic: str):
    """模拟单个用户会话"""
    print(f"用户 {user_id} 开始会话，话题: {topic}")
    
    async with aiohttp.ClientSession() as session:
        # 发起讨论请求
        discuss_data = {"topic": topic}
        async with session.post(
            "http://localhost:8000/api/discuss",
            json=discuss_data
        ) as response:
            if response.status == 200:
                result = await response.json()
                session_id = result["session_id"]
                print(f"用户 {user_id} 获得会话ID: {session_id}")
                
                # 轮询状态直到完成
                max_attempts = 60  # 最多等待60秒
                attempts = 0
                
                while attempts < max_attempts:
                    async with session.get(
                        f"http://localhost:8000/api/discuss/{session_id}/status"
                    ) as status_response:
                        if status_response.status == 200:
                            status_data = await status_response.json()
                            progress = status_data.get("progress", 0)
                            status = status_data.get("status", "processing")
                            
                            print(f"用户 {user_id} 进度: {progress:.2%} ({status})")
                            
                            if status == "completed":
                                print(f"用户 {user_id} 讨论完成!")
                                break
                            elif status == "error":
                                print(f"用户 {user_id} 讨论出错!")
                                break
                        
                        attempts += 1
                        await asyncio.sleep(2)  # 每2秒检查一次
                
                if attempts >= max_attempts:
                    print(f"用户 {user_id} 讨论超时!")
            else:
                print(f"用户 {user_id} 发起讨论失败: {response.status}")

async def test_concurrent_users():
    """测试多用户并发"""
    print("🚀 开始多用户并发测试...")
    print("=" * 50)
    
    # 定义多个用户的话题
    topics = [
        "人工智能在医疗领域的应用",
        "区块链技术的未来发展",
        "可持续能源解决方案",
        "数字化转型策略",
        "智能城市基础设施建设"
    ]
    
    # 创建并发任务
    tasks = []
    for i, topic in enumerate(topics):
        user_id = i + 1
        task = asyncio.create_task(simulate_user_session(user_id, topic))
        tasks.append(task)
    
    # 等待所有任务完成
    start_time = time.time()
    await asyncio.gather(*tasks)
    end_time = time.time()
    
    print("=" * 50)
    print(f"✅ 多用户并发测试完成，总耗时: {end_time - start_time:.2f}秒")
    print("📊 请检查控制台日志和logs目录下的会话日志文件")
    print("🔍 每个会话都有独立的日志文件，格式: logs/session_<session_id>.log")

if __name__ == "__main__":
    print("多用户并发日志测试工具")
    print("请确保服务器已启动: python startup.py")
    print()
    
    # 运行测试
    asyncio.run(test_concurrent_users())
