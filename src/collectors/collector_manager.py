#!/usr/bin/env python3
"""
收集器管理器
用于管理和协调各个日志收集器
"""

from collectors.access_log_collector import AccessLogCollector
from collectors.alert_log_collector import AlertLogCollector
from collectors.disk_info_collector import DiskInfoCollector
from collectors.system_metrics_collector import SystemMetricsCollector

class CollectorManager:
    """收集器管理器"""
    
    def __init__(self, config, telegram_bot=None):
        """
        初始化收集器管理器
        
        Args:
            config: 配置对象
            telegram_bot: Telegram 机器人实例（用于实时推送）
        """
        self.config = config
        self.telegram_bot = telegram_bot
        self.collectors = {}
        self._init_collectors()
    
    def _init_collectors(self):
        """
        初始化各个收集器
        """
        # 系统访问日志收集器
        if self.config.collectors.access_log and self.config.collectors.access_log.enabled:
            self.collectors['access_log'] = AccessLogCollector(self.config, self.telegram_bot)
            # 启动实时监控
            self.collectors['access_log'].start_real_time_monitoring()
        
        # 系统告警日志收集器
        if self.config.collectors.alert_log and self.config.collectors.alert_log.enabled:
            self.collectors['alert_log'] = AlertLogCollector(self.config)
        
        # 硬盘信息收集器
        if self.config.collectors.disk_info and self.config.collectors.disk_info.enabled:
            self.collectors['disk_info'] = DiskInfoCollector(self.config)
        
        # 系统性能指标收集器
        if self.config.collectors.system_metrics and self.config.collectors.system_metrics.enabled:
            self.collectors['system_metrics'] = SystemMetricsCollector(self.config)
    
    def start_real_time_monitoring(self):
        """
        启动所有收集器的实时监控
        """
        if 'access_log' in self.collectors:
            self.collectors['access_log'].start_real_time_monitoring()
    
    def stop_real_time_monitoring(self):
        """
        停止所有收集器的实时监控
        """
        if 'access_log' in self.collectors:
            self.collectors['access_log'].stop_real_time_monitoring()
    
    def collect(self, collector_name):
        """
        执行指定收集器的收集操作
        
        Args:
            collector_name: 收集器名称
            
        Returns:
            dict: 收集到的数据
        """
        if collector_name in self.collectors:
            return self.collectors[collector_name].collect()
        return None
    
    def collect_all(self):
        """
        执行所有收集器的收集操作
        
        Returns:
            dict: 所有收集器收集到的数据
        """
        all_data = {}
        for name, collector in self.collectors.items():
            all_data[name] = collector.collect()
        return all_data
