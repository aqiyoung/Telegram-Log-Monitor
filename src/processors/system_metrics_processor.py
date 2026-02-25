#!/usr/bin/env python3
"""
系统性能指标处理器
用于处理和格式化系统性能指标数据
"""

class SystemMetricsProcessor:
    """系统性能指标处理器"""
    
    def __init__(self, config):
        """
        初始化系统性能指标处理器
        
        Args:
            config: 配置对象
        """
        self.config = config
    
    def process(self, data):
        """
        处理系统性能指标数据
        
        Args:
            data: 收集到的系统性能指标数据
            
        Returns:
            dict: 处理后的系统性能指标数据
        """
        if not data or data.get('status') != 'success':
            return data
        
        # 获取原始数据
        cpu_usage = data.get('cpu_usage', {})
        memory_usage = data.get('memory_usage', {})
        network_stats = data.get('network_stats', {})
        system_load = data.get('system_load', {})
        
        # 过滤和优先级分类
        prioritized_metrics = self._prioritize_metrics(
            cpu_usage, memory_usage, network_stats, system_load
        )
        
        # 格式化数据
        formatted_metrics = self._format_metrics(prioritized_metrics)
        
        # 构建处理后的结果
        processed_data = {
            'status': 'success',
            'prioritized_metrics': prioritized_metrics,
            'formatted_message': formatted_metrics
        }
        
        return processed_data
    
    def _prioritize_metrics(self, cpu_usage, memory_usage, network_stats, system_load):
        """
        系统性能指标优先级分类
        
        Args:
            cpu_usage: CPU 使用率信息
            memory_usage: 内存使用情况信息
            network_stats: 网络流量信息
            system_load: 系统负载信息
            
        Returns:
            dict: 按优先级分类的系统性能指标
        """
        # 优先级分类
        prioritized = {
            'high': [],  # 高优先级
            'medium': [],  # 中优先级
            'low': []  # 低优先级
        }
        
        # CPU 使用率
        cpu_total = cpu_usage.get('total', 0)
        if cpu_total >= self.config.thresholds.cpu_usage:
            prioritized['high'].append({
                'type': 'cpu',
                'metric': 'usage',
                'value': cpu_total,
                'message': f"CPU 使用率过高: {cpu_total:.1f}%"
            })
        elif cpu_total >= self.config.thresholds.cpu_usage - 20:
            prioritized['medium'].append({
                'type': 'cpu',
                'metric': 'usage',
                'value': cpu_total,
                'message': f"CPU 使用率较高: {cpu_total:.1f}%"
            })
        else:
            prioritized['low'].append({
                'type': 'cpu',
                'metric': 'usage',
                'value': cpu_total,
                'message': f"CPU 使用率正常: {cpu_total:.1f}%"
            })
        
        # 内存使用率
        memory_percent = memory_usage.get('virtual', {}).get('percent', 0)
        if memory_percent >= self.config.thresholds.memory_usage:
            prioritized['high'].append({
                'type': 'memory',
                'metric': 'usage',
                'value': memory_percent,
                'message': f"内存使用率过高: {memory_percent:.1f}%"
            })
        elif memory_percent >= self.config.thresholds.memory_usage - 20:
            prioritized['medium'].append({
                'type': 'memory',
                'metric': 'usage',
                'value': memory_percent,
                'message': f"内存使用率较高: {memory_percent:.1f}%"
            })
        else:
            prioritized['low'].append({
                'type': 'memory',
                'metric': 'usage',
                'value': memory_percent,
                'message': f"内存使用率正常: {memory_percent:.1f}%"
            })
        
        # 系统负载
        load_1min = system_load.get('1min', 0)
        if load_1min > 1.0:
            prioritized['medium'].append({
                'type': 'system',
                'metric': 'load',
                'value': load_1min,
                'message': f"系统负载较高: {load_1min:.2f}"
            })
        else:
            prioritized['low'].append({
                'type': 'system',
                'metric': 'load',
                'value': load_1min,
                'message': f"系统负载正常: {load_1min:.2f}"
            })
        
        # 网络流量（只作为参考）
        bytes_sent_per_sec = network_stats.get('bytes_sent_per_sec', 0)
        bytes_recv_per_sec = network_stats.get('bytes_recv_per_sec', 0)
        prioritized['low'].append({
            'type': 'network',
            'metric': 'traffic',
            'sent': bytes_sent_per_sec,
            'recv': bytes_recv_per_sec,
            'message': f"网络流量: 发送 {bytes_sent_per_sec:.2f} B/s, 接收 {bytes_recv_per_sec:.2f} B/s"
        })
        
        return prioritized
    
    def _format_metrics(self, prioritized_metrics):
        """
        格式化系统性能指标为消息
        
        Args:
            prioritized_metrics: 按优先级分类的系统性能指标
            
        Returns:
            str: 格式化后的消息
        """
        message_parts = []
        message_parts.append("⚡ **系统性能指标报告**")
        message_parts.append("")
        
        # 高优先级指标
        if prioritized_metrics.get('high'):
            message_parts.append("🔴 **高优先级**")
            for metric in prioritized_metrics['high']:
                message_parts.append(f"- {metric.get('message')}")
            message_parts.append("")
        
        # 中优先级指标
        if prioritized_metrics.get('medium'):
            message_parts.append("🟡 **中优先级**")
            for metric in prioritized_metrics['medium']:
                message_parts.append(f"- {metric.get('message')}")
            message_parts.append("")
        
        # 低优先级指标
        if prioritized_metrics.get('low'):
            message_parts.append("🟢 **低优先级**")
            for metric in prioritized_metrics['low']:
                message_parts.append(f"- {metric.get('message')}")
            message_parts.append("")
        
        return "\n".join(message_parts)
