#!/usr/bin/env python3
"""
文件监控工具类
用于实时监控日志文件的变化
"""

import time
import threading
import logging

# 尝试导入 watchdog 模块
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    logging.warning("watchdog 模块未安装，实时监控功能将不可用")
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = object

class LogFileWatcher:
    """
    日志文件监控器
    """
    
    def __init__(self, file_path, callback):
        """
        初始化日志文件监控器
        
        Args:
            file_path: 要监控的日志文件路径
            callback: 日志变化时的回调函数
        """
        self.file_path = file_path
        self.callback = callback
        self.observer = None
        self.running = False
        self.file_position = 0
        self.lock = threading.Lock()
    
    def start(self):
        """
        开始监控
        """
        if self.running:
            return
        
        # 检查 watchdog 模块是否可用
        if not WATCHDOG_AVAILABLE:
            logging.warning("watchdog 模块未安装，无法启动实时监控")
            return
        
        self.running = True
        
        # 记录文件当前位置
        try:
            with open(self.file_path, 'r') as f:
                f.seek(0, 2)
                self.file_position = f.tell()
        except Exception as e:
            logging.error(f"获取文件位置失败: {e}")
        
        # 创建事件处理器
        event_handler = LogFileHandler(self.file_path, self.file_position, self.callback, self.lock)
        
        # 创建观察者
        self.observer = Observer()
        
        # 监控文件所在目录
        directory = "/" if self.file_path == "/" else self.file_path.rpartition("/")[0]
        
        try:
            self.observer.schedule(event_handler, directory, recursive=False)
            self.observer.start()
            logging.info(f"开始监控日志文件: {self.file_path}")
        except Exception as e:
            logging.error(f"启动文件监控失败: {e}")
            self.running = False
    
    def stop(self):
        """
        停止监控
        """
        if not self.running:
            return
        
        self.running = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=5)
            logging.info(f"停止监控日志文件: {self.file_path}")

class LogFileHandler(FileSystemEventHandler):
    """
    日志文件事件处理器
    """
    
    def __init__(self, file_path, initial_position, callback, lock):
        """
        初始化日志文件事件处理器
        
        Args:
            file_path: 要监控的日志文件路径
            initial_position: 文件初始位置
            callback: 日志变化时的回调函数
            lock: 线程锁
        """
        self.file_path = file_path
        self.file_position = initial_position
        self.callback = callback
        self.lock = lock
    
    def on_modified(self, event):
        """
        文件修改事件
        
        Args:
            event: 文件系统事件
        """
        if event.is_directory:
            return
        
        if event.src_path == self.file_path:
            self._process_file_change()
    
    def on_created(self, event):
        """
        文件创建事件
        
        Args:
            event: 文件系统事件
        """
        if event.is_directory:
            return
        
        if event.src_path == self.file_path:
            # 文件被重新创建，重置文件位置
            self.file_position = 0
            self._process_file_change()
    
    def _process_file_change(self):
        """
        处理文件变化
        """
        with self.lock:
            try:
                with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    # 移动到上次读取的位置
                    f.seek(self.file_position)
                    
                    # 读取新内容
                    new_content = f.read()
                    
                    # 更新文件位置
                    self.file_position = f.tell()
                    
                    # 如果有新内容，调用回调函数
                    if new_content:
                        self.callback(new_content)
                        
            except Exception as e:
                logging.error(f"处理文件变化失败: {e}")
