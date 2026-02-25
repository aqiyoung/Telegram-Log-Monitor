#!/usr/bin/env python3
"""
硬盘信息处理器
用于处理和格式化硬盘信息数据
"""

class DiskInfoProcessor:
    """硬盘信息处理器"""
    
    def __init__(self, config):
        """
        初始化硬盘信息处理器
        
        Args:
            config: 配置对象
        """
        self.config = config
    
    def process(self, data):
        """
        处理硬盘信息数据
        
        Args:
            data: 收集到的硬盘信息数据
            
        Returns:
            dict: 处理后的硬盘信息数据
        """
        if not data or data.get('status') != 'success':
            return data
        
        # 获取原始数据
        disk_usage = data.get('disk_usage', [])
        disk_health = data.get('disk_health', [])
        
        # 过滤和优先级分类
        filtered_usage = self._filter_disk_usage(disk_usage)
        prioritized_usage = self._prioritize_disk_usage(filtered_usage)
        
        filtered_health = self._filter_disk_health(disk_health)
        prioritized_health = self._prioritize_disk_health(filtered_health)
        
        # 格式化数据
        formatted_info = self._format_disk_info(prioritized_usage, prioritized_health)
        
        # 构建处理后的结果
        processed_data = {
            'status': 'success',
            'disk_usage_count': len(disk_usage),
            'disk_health_count': len(disk_health),
            'prioritized_usage': prioritized_usage,
            'prioritized_health': prioritized_health,
            'formatted_message': formatted_info
        }
        
        return processed_data
    
    def _filter_disk_usage(self, disk_usage):
        """
        过滤磁盘使用情况
        
        Args:
            disk_usage: 原始磁盘使用情况列表
            
        Returns:
            list: 过滤后的磁盘使用情况列表
        """
        # 过滤掉使用率低的磁盘
        filtered_usage = []
        
        for disk in disk_usage:
            # 只保留使用率超过阈值的磁盘
            if disk.get('percent', 0) >= self.config.thresholds.disk_usage - 10:
                filtered_usage.append(disk)
        
        return filtered_usage
    
    def _prioritize_disk_usage(self, disk_usage):
        """
        磁盘使用情况优先级分类
        
        Args:
            disk_usage: 过滤后的磁盘使用情况列表
            
        Returns:
            dict: 按优先级分类的磁盘使用情况
        """
        # 优先级分类
        prioritized = {
            'high': [],  # 高优先级
            'medium': [],  # 中优先级
            'low': []  # 低优先级
        }
        
        for disk in disk_usage:
            usage_percent = disk.get('percent', 0)
            if usage_percent >= self.config.thresholds.disk_usage:
                # 超过阈值为高优先级
                prioritized['high'].append(disk)
            elif usage_percent >= self.config.thresholds.disk_usage - 10:
                # 接近阈值为中优先级
                prioritized['medium'].append(disk)
            else:
                # 其他为低优先级
                prioritized['low'].append(disk)
        
        return prioritized
    
    def _filter_disk_health(self, disk_health):
        """
        过滤磁盘健康状态
        
        Args:
            disk_health: 原始磁盘健康状态列表
            
        Returns:
            list: 过滤后的磁盘健康状态列表
        """
        # 过滤掉健康状态良好的磁盘
        filtered_health = []
        
        for disk in disk_health:
            # 只保留状态不是良好的磁盘或温度接近阈值的磁盘
            status = disk.get('status', '').lower()
            temperature = disk.get('temperature')
            
            if (status != 'ok' and status != 'healthy') or \
               (temperature and temperature >= self.config.thresholds.disk_temperature - 10):
                filtered_health.append(disk)
        
        return filtered_health
    
    def _prioritize_disk_health(self, disk_health):
        """
        磁盘健康状态优先级分类
        
        Args:
            disk_health: 过滤后的磁盘健康状态列表
            
        Returns:
            dict: 按优先级分类的磁盘健康状态
        """
        # 优先级分类
        prioritized = {
            'high': [],  # 高优先级
            'medium': [],  # 中优先级
            'low': []  # 低优先级
        }
        
        for disk in disk_health:
            status = disk.get('status', '').lower()
            temperature = disk.get('temperature')
            
            if (status != 'ok' and status != 'healthy') or \
               (temperature and temperature >= self.config.thresholds.disk_temperature):
                # 状态异常或温度超过阈值为高优先级
                prioritized['high'].append(disk)
            elif temperature and temperature >= self.config.thresholds.disk_temperature - 10:
                # 温度接近阈值为中优先级
                prioritized['medium'].append(disk)
            else:
                # 其他为低优先级
                prioritized['low'].append(disk)
        
        return prioritized
    
    def _format_disk_info(self, prioritized_usage, prioritized_health):
        """
        格式化磁盘信息为消息
        
        Args:
            prioritized_usage: 按优先级分类的磁盘使用情况
            prioritized_health: 按优先级分类的磁盘健康状态
            
        Returns:
            str: 格式化后的消息
        """
        message_parts = []
        message_parts.append("💾 **硬盘信息报告**")
        message_parts.append("")
        
        # 磁盘使用情况
        if any(prioritized_usage.values()):
            message_parts.append("📊 **磁盘使用情况**")
            
            # 高优先级
            if prioritized_usage.get('high'):
                message_parts.append("🔴 **高优先级**")
                for disk in prioritized_usage['high']:
                    usage_percent = disk.get('percent', 0)
                    message_parts.append(f"- {disk.get('device')} ({disk.get('mountpoint')}): {usage_percent:.1f}%")
                message_parts.append("")
            
            # 中优先级
            if prioritized_usage.get('medium'):
                message_parts.append("🟡 **中优先级**")
                for disk in prioritized_usage['medium']:
                    usage_percent = disk.get('percent', 0)
                    message_parts.append(f"- {disk.get('device')} ({disk.get('mountpoint')}): {usage_percent:.1f}%")
                message_parts.append("")
        
        # 磁盘健康状态
        if any(prioritized_health.values()):
            message_parts.append("🏥 **磁盘健康状态**")
            
            # 高优先级
            if prioritized_health.get('high'):
                message_parts.append("🔴 **高优先级**")
                for disk in prioritized_health['high']:
                    status = disk.get('status', '未知')
                    temperature = disk.get('temperature')
                    temp_str = f" | 温度: {temperature}°C" if temperature else ""
                    message_parts.append(f"- {disk.get('device')}: 状态={status}{temp_str}")
                message_parts.append("")
            
            # 中优先级
            if prioritized_health.get('medium'):
                message_parts.append("🟡 **中优先级**")
                for disk in prioritized_health['medium']:
                    status = disk.get('status', '未知')
                    temperature = disk.get('temperature')
                    temp_str = f" | 温度: {temperature}°C" if temperature else ""
                    message_parts.append(f"- {disk.get('device')}: 状态={status}{temp_str}")
                message_parts.append("")
        
        # 如果没有重要信息
        if len(message_parts) <= 2:
            return "💾 **硬盘信息报告**\n\n所有硬盘状态正常，使用率在安全范围内。"
        
        return "\n".join(message_parts)
