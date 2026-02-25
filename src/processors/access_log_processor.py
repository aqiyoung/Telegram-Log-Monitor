#!/usr/bin/env python3
"""
系统访问日志处理器
用于处理和格式化系统访问日志数据
"""

class AccessLogProcessor:
    """系统访问日志处理器"""
    
    def __init__(self, config):
        """
        初始化访问日志处理器
        
        Args:
            config: 配置对象
        """
        self.config = config
    
    def process(self, data):
        """
        处理访问日志数据
        
        Args:
            data: 收集到的访问日志数据
            
        Returns:
            dict: 处理后的访问日志数据
        """
        if not data or data.get('status') != 'success':
            return data
        
        # 获取原始数据
        raw_logs = data.get('data', [])
        
        # 过滤和优先级分类
        filtered_logs = self._filter_logs(raw_logs)
        prioritized_logs = self._prioritize_logs(filtered_logs)
        
        # 格式化数据
        formatted_logs = self._format_logs(prioritized_logs)
        
        # 构建处理后的结果
        processed_data = {
            'status': 'success',
            'original_count': len(raw_logs),
            'filtered_count': len(filtered_logs),
            'prioritized_logs': prioritized_logs,
            'formatted_message': formatted_logs
        }
        
        return processed_data
    
    def _filter_logs(self, logs):
        """
        过滤日志
        
        Args:
            logs: 原始日志列表
            
        Returns:
            list: 过滤后的日志列表
        """
        # 过滤掉无关的日志
        filtered_logs = []
        
        for log in logs:
            # 只保留重要的登录相关日志
            if log.get('action') in ['登录成功', '登录失败', '无效用户']:
                filtered_logs.append(log)
        
        return filtered_logs
    
    def _prioritize_logs(self, logs):
        """
        优先级分类
        
        Args:
            logs: 过滤后的日志列表
            
        Returns:
            dict: 按优先级分类的日志
        """
        # 优先级分类
        prioritized = {
            'high': [],  # 高优先级
            'medium': [],  # 中优先级
            'low': []  # 低优先级
        }
        
        for log in logs:
            action = log.get('action')
            if action == '登录失败' or action == '无效用户':
                # 登录失败和无效用户为高优先级
                prioritized['high'].append(log)
            elif action == '登录成功':
                # 登录成功为中优先级
                prioritized['medium'].append(log)
            else:
                # 其他为低优先级
                prioritized['low'].append(log)
        
        return prioritized
    
    def _format_logs(self, prioritized_logs):
        """
        格式化日志为消息
        
        Args:
            prioritized_logs: 按优先级分类的日志
            
        Returns:
            str: 格式化后的消息
        """
        if not any(prioritized_logs.values()):
            return "没有重要的系统访问日志"
        
        # 构建格式化消息
        message_parts = []
        message_parts.append("📊 **系统访问日志报告**")
        message_parts.append("")
        
        # 高优先级日志
        if prioritized_logs.get('high'):
            message_parts.append("🚨 **高优先级**")
            for log in prioritized_logs['high']:
                message_parts.append(f"- {log.get('action')}: {log.get('user')}")
            message_parts.append("")
        
        # 中优先级日志
        if prioritized_logs.get('medium'):
            message_parts.append("⚠️ **中优先级**")
            for log in prioritized_logs['medium']:
                message_parts.append(f"- {log.get('action')}: {log.get('user')}")
            message_parts.append("")
        
        # 低优先级日志
        if prioritized_logs.get('low'):
            message_parts.append("ℹ️ **低优先级**")
            for log in prioritized_logs['low']:
                message_parts.append(f"- {log.get('action')}: {log.get('user')}")
            message_parts.append("")
        
        return "\n".join(message_parts)
