#!/usr/bin/env python3
"""
系统访问日志收集器
用于收集系统访问日志，如用户登录、文件访问等操作
"""

import os
import re
import threading
from datetime import datetime, timedelta

from utils.file_watcher import LogFileWatcher

class AccessLogCollector:
    """系统访问日志收集器"""
    
    def __init__(self, config, telegram_bot=None):
        """
        初始化访问日志收集器
        
        Args:
            config: 配置对象
            telegram_bot: Telegram 机器人实例（用于实时推送）
        """
        self.config = config
        self.telegram_bot = telegram_bot
        self.log_path = config.collectors.access_log.log_path
        self.last_collect_time = datetime.now() - timedelta(seconds=config.collectors.access_log.collect_interval)
        self.file_watcher = None
        self.watcher_thread = None
        self.running = False
    
    def start_real_time_monitoring(self):
        """
        启动实时监控
        """
        if self.running:
            return
        
        self.running = True
        
        # 检查日志文件是否存在
        if not os.path.exists(self.log_path):
            return
        
        # 创建文件监控器
        self.file_watcher = LogFileWatcher(self.log_path, self._on_log_change)
        
        # 启动监控线程
        self.watcher_thread = threading.Thread(target=self.file_watcher.start, daemon=True)
        self.watcher_thread.start()
    
    def stop_real_time_monitoring(self):
        """
        停止实时监控
        """
        if not self.running:
            return
        
        self.running = False
        
        if self.file_watcher:
            self.file_watcher.stop()
        
        if self.watcher_thread:
            self.watcher_thread.join(timeout=5)
    
    def _on_log_change(self, new_content):
        """
        处理日志文件变化
        
        Args:
            new_content: 新的日志内容
        """
        try:
            # 按行分割日志
            log_lines = new_content.strip().split('\n')
            
            # 解析每行日志
            for log_line in log_lines:
                # 提取登录事件
                login_event = self._extract_login_event(log_line)
                if login_event:
                    # 发送实时通知
                    self._send_login_notification(login_event)
        except Exception as e:
            import logging
            logging.error(f"处理日志变化失败: {e}")
    
    def _extract_login_event(self, log_line):
        """
        提取登录事件
        
        Args:
            log_line: 日志行
            
        Returns:
            dict: 登录事件信息
        """
        # 登录相关模式
        login_patterns = [
            (r'Accepted\s+(\w+)\s+for\s+(\w+)', '登录成功'),
            (r'Failed\s+password\s+for\s+(\w+)', '登录失败'),
            (r'Invalid\s+user\s+(\w+)', '无效用户')
        ]
        
        for pattern, action in login_patterns:
            match = re.search(pattern, log_line)
            if match:
                if len(match.groups()) == 2:
                    method, user = match.groups()
                else:
                    method = '未知'
                    user = match.group(1)
                
                return {
                    'action': action,
                    'user': user,
                    'method': method,
                    'details': log_line,
                    'timestamp': self._parse_log_time(log_line)
                }
        
        return None
    
    def _send_login_notification(self, login_event):
        """
        发送登录通知
        
        Args:
            login_event: 登录事件信息
        """
        if not self.telegram_bot:
            return
        
        # 构建通知消息
        action = login_event.get('action')
        user = login_event.get('user')
        method = login_event.get('method')
        timestamp = login_event.get('timestamp')
        
        # 时间格式化
        time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S') if timestamp else '未知时间'
        
        # 根据登录事件类型构建消息
        if action == '登录成功':
            message = f"🚨 **登录通知**\n\n" \
                      f"**时间**: {time_str}\n" \
                      f"**事件**: {action}\n" \
                      f"**用户**: {user}\n" \
                      f"**方式**: {method}\n" \
                      f"**详情**: {login_event.get('details', '')}"
            severity = 'warning'
        else:
            message = f"🚨 **安全告警**\n\n" \
                      f"**时间**: {time_str}\n" \
                      f"**事件**: {action}\n" \
                      f"**用户**: {user}\n" \
                      f"**详情**: {login_event.get('details', '')}"
            severity = 'error'
        
        # 发送通知
        self.telegram_bot.send_alert(message, severity=severity)
    
    def collect(self):
        """
        收集访问日志
        
        Returns:
            dict: 收集到的访问日志数据
        """
        try:
            if not os.path.exists(self.log_path):
                return {
                    'status': 'error',
                    'message': f"日志文件不存在: {self.log_path}"
                }
            
            # 读取日志文件
            with open(self.log_path, 'r', encoding='utf-8', errors='ignore') as f:
                logs = f.readlines()
            
            # 过滤出最近的日志
            recent_logs = []
            for log in logs:
                # 解析日志时间戳
                log_time = self._parse_log_time(log)
                if log_time and log_time > self.last_collect_time:
                    recent_logs.append(log.strip())
            
            # 更新最后收集时间
            self.last_collect_time = datetime.now()
            
            # 提取关键信息
            parsed_logs = self._parse_logs(recent_logs)
            
            return {
                'status': 'success',
                'data': parsed_logs,
                'count': len(parsed_logs)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _parse_log_time(self, log_line):
        """
        解析日志时间戳
        
        Args:
            log_line: 日志行
            
        Returns:
            datetime: 日志时间
        """
        # Debian 系统 auth.log 格式示例: Feb 25 10:00:00 hostname sshd[1234]: ...
        pattern = r'^(\w{3})\s+(\d{1,2})\s+(\d{2}):(\d{2}):(\d{2})'
        match = re.match(pattern, log_line)
        if not match:
            return None
        
        month, day, hour, minute, second = match.groups()
        
        # 获取当前年份
        year = datetime.now().year
        
        # 构建日期时间对象
        try:
            # 月份映射
            month_map = {
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
                'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
                'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }
            month_num = month_map.get(month)
            if not month_num:
                return None
            
            return datetime(year, month_num, int(day), int(hour), int(minute), int(second))
        except Exception:
            return None
    
    def _parse_logs(self, logs):
        """
        解析日志，提取关键信息
        
        Args:
            logs: 日志列表
            
        Returns:
            list: 解析后的日志信息
        """
        parsed_logs = []
        
        # 登录相关模式
        login_patterns = [
            (r'Accepted\s+\w+\s+for\s+(\w+)', '登录成功'),
            (r'Failed\s+password\s+for\s+(\w+)', '登录失败'),
            (r'Invalid\s+user\s+(\w+)', '无效用户'),
            (r'session\s+opened\s+for\s+user\s+(\w+)', '会话打开'),
            (r'session\s+closed\s+for\s+user\s+(\w+)', '会话关闭')
        ]
        
        for log in logs:
            for pattern, action in login_patterns:
                match = re.search(pattern, log)
                if match:
                    user = match.group(1) if len(match.groups()) > 0 else '未知'
                    parsed_logs.append({
                        'action': action,
                        'user': user,
                        'details': log
                    })
                    break
        
        return parsed_logs
