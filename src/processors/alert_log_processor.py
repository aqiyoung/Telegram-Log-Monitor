#!/usr/bin/env python3
"""
系统告警日志处理器
用于处理和格式化系统告警日志数据
"""

class AlertLogProcessor:
    """系统告警日志处理器"""
    
    def __init__(self, config):
        """
        初始化告警日志处理器
        
        Args:
            config: 配置对象
        """
        self.config = config
    
    def process(self, data):
        """
        处理告警日志数据
        
        Args:
            data: 收集到的告警日志数据
            
        Returns:
            dict: 处理后的告警日志数据
        """
        if not data or data.get('status') != 'success':
            return data
        
        # 获取原始数据
        raw_alerts = data.get('data', [])
        
        # 过滤和优先级分类
        filtered_alerts = self._filter_alerts(raw_alerts)
        prioritized_alerts = self._prioritize_alerts(filtered_alerts)
        
        # 格式化数据
        formatted_alerts = self._format_alerts(prioritized_alerts)
        
        # 构建处理后的结果
        processed_data = {
            'status': 'success',
            'original_count': len(raw_alerts),
            'filtered_count': len(filtered_alerts),
            'prioritized_alerts': prioritized_alerts,
            'formatted_message': formatted_alerts
        }
        
        return processed_data
    
    def _filter_alerts(self, alerts):
        """
        过滤告警
        
        Args:
            alerts: 原始告警列表
            
        Returns:
            list: 过滤后的告警列表
        """
        # 过滤掉无关的告警
        filtered_alerts = []
        
        for alert in alerts:
            # 只保留重要级别的告警
            if alert.get('level') in ['致命', '严重', '错误', '警告', '告警']:
                filtered_alerts.append(alert)
        
        return filtered_alerts
    
    def _prioritize_alerts(self, alerts):
        """
        优先级分类
        
        Args:
            alerts: 过滤后的告警列表
            
        Returns:
            dict: 按优先级分类的告警
        """
        # 优先级分类
        prioritized = {
            'high': [],  # 高优先级
            'medium': [],  # 中优先级
            'low': []  # 低优先级
        }
        
        # 级别到优先级的映射
        level_priority = {
            '致命': 'high',
            '严重': 'high',
            '错误': 'medium',
            '警告': 'medium',
            '告警': 'low'
        }
        
        for alert in alerts:
            level = alert.get('level')
            priority = level_priority.get(level, 'low')
            prioritized[priority].append(alert)
        
        return prioritized
    
    def _format_alerts(self, prioritized_alerts):
        """
        格式化告警为消息
        
        Args:
            prioritized_alerts: 按优先级分类的告警
            
        Returns:
            str: 格式化后的消息
        """
        if not any(prioritized_alerts.values()):
            return "没有重要的系统告警日志"
        
        # 构建格式化消息
        message_parts = []
        message_parts.append("🚨 **系统告警日志报告**")
        message_parts.append("")
        
        # 高优先级告警
        if prioritized_alerts.get('high'):
            message_parts.append("🔴 **高优先级**")
            for alert in prioritized_alerts['high']:
                message_parts.append(f"- [{alert.get('service')}] {alert.get('level')}: {alert.get('message')[:100]}...")
            message_parts.append("")
        
        # 中优先级告警
        if prioritized_alerts.get('medium'):
            message_parts.append("🟡 **中优先级**")
            for alert in prioritized_alerts['medium']:
                message_parts.append(f"- [{alert.get('service')}] {alert.get('level')}: {alert.get('message')[:100]}...")
            message_parts.append("")
        
        # 低优先级告警
        if prioritized_alerts.get('low'):
            message_parts.append("🟢 **低优先级**")
            for alert in prioritized_alerts['low']:
                message_parts.append(f"- [{alert.get('service')}] {alert.get('level')}: {alert.get('message')[:100]}...")
            message_parts.append("")
        
        return "\n".join(message_parts)
