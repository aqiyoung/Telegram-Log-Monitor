#!/usr/bin/env python3
"""
系统告警日志收集器
用于收集系统告警日志，如错误提示、异常状态等警告信息
"""

import os
import re
from datetime import datetime, timedelta

class AlertLogCollector:
    """系统告警日志收集器"""
    
    def __init__(self, config):
        """
        初始化告警日志收集器
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.log_path = config.collectors.alert_log.log_path
        self.last_collect_time = datetime.now() - timedelta(seconds=config.collectors.alert_log.collect_interval)
    
    def collect(self):
        """
        收集告警日志
        
        Returns:
            dict: 收集到的告警日志数据
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
            
            # 提取关键告警信息
            parsed_alerts = self._parse_alerts(recent_logs)
            
            return {
                'status': 'success',
                'data': parsed_alerts,
                'count': len(parsed_alerts)
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
        # Debian 系统 syslog 格式示例: Feb 25 10:00:00 hostname service[1234]: ...
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
    
    def _parse_alerts(self, logs):
        """
        解析告警日志，提取关键信息
        
        Args:
            logs: 日志列表
            
        Returns:
            list: 解析后的告警信息
        """
        parsed_alerts = []
        
        # 告警级别关键字
        alert_levels = {
            'ERROR': '错误',
            'WARN': '警告',
            'WARNING': '警告',
            'CRITICAL': '严重',
            'FATAL': '致命',
            'ALERT': '告警'
        }
        
        # 关键服务关键字
        critical_services = [
            'sshd', 'sudo', 'fail2ban', 'systemd', 'kernel',
            'disk', 'mount', 'network', 'smbd', 'nginx', 'apache'
        ]
        
        for log in logs:
            # 检测告警级别
            alert_level = '信息'
            for level_key, level_name in alert_levels.items():
                if level_key in log:
                    alert_level = level_name
                    break
            
            # 检测关键服务
            service = '未知'
            for srv in critical_services:
                if f'{srv}[' in log or f'{srv}:' in log:
                    service = srv
                    break
            
            # 提取告警消息
            message = log
            
            # 构建告警信息
            parsed_alerts.append({
                'level': alert_level,
                'service': service,
                'message': message
            })
        
        # 按告警级别排序（严重程度从高到低）
        level_order = ['致命', '严重', '错误', '警告', '告警', '信息']
        parsed_alerts.sort(key=lambda x: level_order.index(x['level']))
        
        return parsed_alerts
