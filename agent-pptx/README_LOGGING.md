# AI Agent讨论系统 - 日志隔离功能说明

## 概述

在多用户并发使用AI Agent讨论系统时，为了解决日志混乱的问题，我们实现了完整的日志隔离功能。现在每个用户会话都有独立的日志记录，便于调试和监控。

## 主要特性

### 1. 会话隔离日志
- 每个会话有独立的日志记录器
- 控制台日志包含会话ID标识：`[Session-<session_id>]`
- 文件日志按会话分离：`logs/session_<session_id>.log`

### 2. Agent级别日志
- 每个Agent都有会话专用的日志记录器
- 日志名称格式：`Session-<session_id>-Agent-<agent_name>`
- 支持Agent级别的日志追踪

### 3. 日志查看工具
- 提供专门的日志查看工具
- 支持按会话查看、搜索和监控
- 实时显示最近活动

## 使用方法

### 1. 启动系统
```bash
# 启动优化后的系统
python startup.py
```

### 2. 多用户并发测试
```bash
# 运行并发测试
python test_concurrent_logging.py
```

### 3. 查看日志
```bash
# 启动日志查看工具
python log_viewer.py
```

## 日志格式

### 控制台日志示例
```
2024-01-15 10:30:15 - [Session-abc123] - Session-abc123 - INFO - 创建新讨论会话，话题: 人工智能应用
2024-01-15 10:30:16 - [Session-abc123] - Session-abc123-Agent-科学家 - INFO - 科学家Agent正在分析话题: 人工智能应用
2024-01-15 10:30:17 - [Session-abc123] - Session-abc123-Agent-科学家 - INFO - 处理输入: 人工智能应用...
2024-01-15 10:30:18 - [Session-def456] - Session-def456 - INFO - 创建新讨论会话，话题: 区块链技术
```

### 文件日志示例
每个会话的日志文件：`logs/session_<session_id>.log`
```
2024-01-15 10:30:15 - Session-abc123 - INFO - 创建新讨论会话，话题: 人工智能应用
2024-01-15 10:30:16 - Session-abc123-Agent-科学家 - INFO - 科学家Agent正在分析话题: 人工智能应用
2024-01-15 10:30:17 - Session-abc123-Agent-科学家 - INFO - 处理输入: 人工智能应用...
2024-01-15 10:30:18 - Session-abc123-Agent-科学家 - INFO - 处理完成
```

## 日志查看工具功能

### 1. 列出所有会话日志
- 显示所有会话日志文件
- 包含文件大小、修改时间等信息
- 按时间倒序排列

### 2. 查看指定会话日志
- 输入会话ID查看详细日志
- 按行号显示日志内容
- 支持大文件查看

### 3. 搜索日志内容
- 支持关键词搜索
- 可指定会话ID或搜索所有会话
- 显示匹配的行号和内容

### 4. 显示最近活动
- 显示最近N分钟的活动
- 按时间倒序排列
- 显示每个会话的最后几行日志

## 技术实现

### 1. 会话日志记录器
```python
def get_session_logger(session_id: str, agent_name: str = None) -> logging.Logger:
    """为指定会话创建独立的日志记录器"""
    if agent_name:
        logger_name = f"Session-{session_id}-Agent-{agent_name}"
    else:
        logger_name = f"Session-{session_id}"
    
    session_logger = logging.getLogger(logger_name)
    # 配置会话专用的日志格式和处理器
```

### 2. Agent日志隔离
```python
def get_logger(self) -> logging.Logger:
    """获取日志记录器 - 优先使用会话专用日志记录器"""
    if hasattr(self, 'session_logger') and self.session_logger:
        return self.session_logger
    return self.logger
```

### 3. 线程安全
- 使用线程锁保护日志记录器创建
- 避免重复添加处理器
- 支持并发访问

## 目录结构

```
agent-pptx/
├── main_optimized.py          # 优化后的主服务器
├── test_concurrent_logging.py # 并发测试工具
├── log_viewer.py             # 日志查看工具
├── logs/                     # 日志目录
│   ├── session_abc123.log    # 会话日志文件
│   ├── session_def456.log    # 会话日志文件
│   └── ...
└── README_LOGGING.md         # 本文档
```

## 故障排除

### 1. 日志文件不存在
- 确保系统已启动并创建了会话
- 检查logs目录是否存在
- 确认会话ID是否正确

### 2. 日志内容为空
- 检查会话是否正常完成
- 确认Agent是否正常执行
- 查看系统错误日志

### 3. 日志格式混乱
- 重启系统清理旧的日志配置
- 检查日志记录器配置
- 确认编码格式为UTF-8

## 性能考虑

### 1. 日志文件大小
- 定期清理过期日志文件
- 监控磁盘空间使用
- 考虑日志轮转机制

### 2. 内存使用
- 避免在内存中保存大量日志
- 及时释放日志记录器
- 监控内存使用情况

### 3. 并发性能
- 使用异步日志记录
- 避免日志记录阻塞主流程
- 合理设置日志级别

## 总结

通过日志隔离功能，系统现在可以：

1. ✅ **清晰区分用户会话**：每个会话有独立的日志标识
2. ✅ **便于问题排查**：可以精确定位到特定会话的问题
3. ✅ **支持并发监控**：实时监控多个用户的推理过程
4. ✅ **提供调试工具**：专门的日志查看和搜索功能
5. ✅ **保证性能**：日志隔离不影响系统性能

这些改进大大提升了系统的可维护性和用户体验，特别是在多用户并发使用的场景下。
