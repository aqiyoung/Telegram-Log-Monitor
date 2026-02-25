#!/usr/bin/env python3
"""
系统性能指标收集器
用于收集系统性能指标，如CPU使用率、内存占用、网络流量等
"""

import psutil
import time

class SystemMetricsCollector:
    """系统性能指标收集器"""
    
    def __init__(self, config):
        """
        初始化系统性能指标收集器
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.last_network_stats = psutil.net_io_counters()
        self.last_collect_time = time.time()
    
    def collect(self):
        """
        收集系统性能指标
        
        Returns:
            dict: 收集到的系统性能指标数据
        """
        try:
            # 收集 CPU 使用率
            cpu_usage = self._collect_cpu_usage()
            
            # 收集内存使用情况
            memory_usage = self._collect_memory_usage()
            
            # 收集网络流量
            network_stats = self._collect_network_stats()
            
            # 收集系统负载
            system_load = self._collect_system_load()
            
            # 更新最后收集时间
            self.last_collect_time = time.time()
            
            return {
                'status': 'success',
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'network_stats': network_stats,
                'system_load': system_load
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _collect_cpu_usage(self):
        """
        收集 CPU 使用率
        
        Returns:
            dict: CPU 使用率信息
        """
        # 获取 CPU 使用率（1秒平均）
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        
        # 计算总使用率
        total_cpu_percent = sum(cpu_percent) / len(cpu_percent)
        
        return {
            'total': total_cpu_percent,
            'per_cpu': cpu_percent
        }
    
    def _collect_memory_usage(self):
        """
        收集内存使用情况
        
        Returns:
            dict: 内存使用情况信息
        """
        # 获取内存使用情况
        memory = psutil.virtual_memory()
        
        # 获取交换内存使用情况
        swap = psutil.swap_memory()
        
        return {
            'virtual': {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent
            },
            'swap': {
                'total': swap.total,
                'used': swap.used,
                'free': swap.free,
                'percent': swap.percent
            }
        }
    
    def _collect_network_stats(self):
        """
        收集网络流量
        
        Returns:
            dict: 网络流量信息
        """
        # 获取当前网络统计数据
        current_stats = psutil.net_io_counters()
        
        # 计算时间差
        time_diff = time.time() - self.last_collect_time
        if time_diff <= 0:
            time_diff = 1
        
        # 计算流量速率
        bytes_sent_per_sec = (current_stats.bytes_sent - self.last_network_stats.bytes_sent) / time_diff
        bytes_recv_per_sec = (current_stats.bytes_recv - self.last_network_stats.bytes_recv) / time_diff
        packets_sent_per_sec = (current_stats.packets_sent - self.last_network_stats.packets_sent) / time_diff
        packets_recv_per_sec = (current_stats.packets_recv - self.last_network_stats.packets_recv) / time_diff
        
        # 更新上次统计数据
        self.last_network_stats = current_stats
        
        return {
            'bytes_sent': current_stats.bytes_sent,
            'bytes_recv': current_stats.bytes_recv,
            'packets_sent': current_stats.packets_sent,
            'packets_recv': current_stats.packets_recv,
            'errin': current_stats.errin,
            'errout': current_stats.errout,
            'dropin': current_stats.dropin,
            'dropout': current_stats.dropout,
            'bytes_sent_per_sec': bytes_sent_per_sec,
            'bytes_recv_per_sec': bytes_recv_per_sec,
            'packets_sent_per_sec': packets_sent_per_sec,
            'packets_recv_per_sec': packets_recv_per_sec
        }
    
    def _collect_system_load(self):
        """
        收集系统负载
        
        Returns:
            dict: 系统负载信息
        """
        # 获取系统负载（仅支持 Unix-like 系统）
        try:
            load_avg = psutil.getloadavg()
            return {
                '1min': load_avg[0],
                '5min': load_avg[1],
                '15min': load_avg[2]
            }
        except Exception:
            # Windows 系统不支持 load average
            return {
                '1min': 0,
                '5min': 0,
                '15min': 0
            }
