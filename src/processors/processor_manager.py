#!/usr/bin/env python3
"""
处理器管理器
用于管理和协调各个数据处理器
"""

from processors.access_log_processor import AccessLogProcessor
from processors.alert_log_processor import AlertLogProcessor
from processors.disk_info_processor import DiskInfoProcessor
from processors.system_metrics_processor import SystemMetricsProcessor

class ProcessorManager:
    """处理器管理器"""
    
    def __init__(self, config):
        """
        初始化处理器管理器
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.processors = {
            'access_log': AccessLogProcessor(config),
            'alert_log': AlertLogProcessor(config),
            'disk_info': DiskInfoProcessor(config),
            'system_metrics': SystemMetricsProcessor(config)
        }
    
    def process(self, collector_name, data):
        """
        处理指定收集器的数据
        
        Args:
            collector_name: 收集器名称
            data: 收集到的数据
            
        Returns:
            dict: 处理后的数据
        """
        if collector_name in self.processors:
            return self.processors[collector_name].process(data)
        return None
    
    def process_all(self, all_data):
        """
        处理所有收集器的数据
        
        Args:
            all_data: 所有收集器收集到的数据
            
        Returns:
            dict: 处理后的所有数据
        """
        processed_data = {}
        for collector_name, data in all_data.items():
            processed_data[collector_name] = self.process(collector_name, data)
        return processed_data
