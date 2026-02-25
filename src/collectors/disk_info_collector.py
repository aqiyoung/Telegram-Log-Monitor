#!/usr/bin/env python3
"""
硬盘信息收集器
用于收集硬盘的容量使用情况、健康状态、温度等SMART数据
"""

import os
import subprocess
import psutil

class DiskInfoCollector:
    """硬盘信息收集器"""
    
    def __init__(self, config):
        """
        初始化硬盘信息收集器
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.smart_enabled = config.collectors.disk_info.smart_enabled
    
    def collect(self):
        """
        收集硬盘信息
        
        Returns:
            dict: 收集到的硬盘信息数据
        """
        try:
            # 收集磁盘使用情况
            disk_usage = self._collect_disk_usage()
            
            # 收集磁盘健康状态和温度（如果启用 SMART）
            disk_health = []
            if self.smart_enabled:
                disk_health = self._collect_disk_health()
            
            return {
                'status': 'success',
                'disk_usage': disk_usage,
                'disk_health': disk_health
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _collect_disk_usage(self):
        """
        收集磁盘使用情况
        
        Returns:
            list: 磁盘使用情况列表
        """
        disk_usage_list = []
        
        # 使用 psutil 获取磁盘分区信息
        for partition in psutil.disk_partitions():
            # 跳过虚拟文件系统和 CD-ROM
            if partition.fstype in ('tmpfs', 'devtmpfs', 'devfs', 'proc', 'sysfs', 'cgroup', 'overlay', 'aufs'):
                continue
            
            # 跳过 CD-ROM 设备
            if 'cdrom' in partition.device.lower():
                continue
            
            try:
                # 获取分区使用情况
                usage = psutil.disk_usage(partition.mountpoint)
                
                # 计算使用率
                usage_percent = usage.percent
                
                # 构建磁盘使用情况信息
                disk_info = {
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage_percent
                }
                
                disk_usage_list.append(disk_info)
                
            except Exception:
                # 跳过无法访问的分区
                pass
        
        return disk_usage_list
    
    def _collect_disk_health(self):
        """
        收集磁盘健康状态和温度（使用 SMART）
        
        Returns:
            list: 磁盘健康状态列表
        """
        disk_health_list = []
        
        # 获取所有磁盘设备
        devices = self._get_disk_devices()
        
        for device in devices:
            try:
                # 检查是否支持 SMART
                if not self._is_smart_supported(device):
                    continue
                
                # 获取 SMART 信息
                smart_info = self._get_smart_info(device)
                
                if smart_info:
                    disk_health_list.append(smart_info)
                    
            except Exception:
                # 跳过无法获取 SMART 信息的设备
                pass
        
        return disk_health_list
    
    def _get_disk_devices(self):
        """
        获取所有磁盘设备
        
        Returns:
            list: 磁盘设备列表
        """
        devices = []
        
        # 检查 /dev 目录下的磁盘设备
        dev_dir = '/dev'
        if os.path.exists(dev_dir):
            for item in os.listdir(dev_dir):
                # 匹配常见的磁盘设备名称
                if item.startswith('sd') or item.startswith('hd') or item.startswith('nvme'):
                    # 只获取主设备（如 sda, hda, nvme0n1），跳过分区（如 sda1）
                    if len(item) <= 3 or (item.startswith('nvme') and 'p' not in item):
                        devices.append(os.path.join(dev_dir, item))
        
        return devices
    
    def _is_smart_supported(self, device):
        """
        检查设备是否支持 SMART
        
        Args:
            device: 设备路径
            
        Returns:
            bool: 是否支持 SMART
        """
        try:
            # 使用 smartctl 命令检查 SMART 支持
            result = subprocess.run(
                ['smartctl', '--all', device],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _get_smart_info(self, device):
        """
        获取设备的 SMART 信息
        
        Args:
            device: 设备路径
            
        Returns:
            dict: SMART 信息
        """
        try:
            # 使用 smartctl 命令获取 SMART 信息
            result = subprocess.run(
                ['smartctl', '--all', device],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return None
            
            output = result.stdout
            
            # 解析 SMART 信息
            smart_info = {
                'device': device,
                'status': '未知',
                'temperature': None,
                'attributes': {}
            }
            
            # 解析健康状态
            if 'SMART overall-health self-assessment test result:' in output:
                status_line = [line for line in output.split('\n') if 'SMART overall-health self-assessment test result:' in line][0]
                status = status_line.split(':')[1].strip()
                smart_info['status'] = status
            
            # 解析温度
            for line in output.split('\n'):
                if 'Temperature_Celsius' in line or 'Temperature:' in line:
                    try:
                        # 提取温度值
                        if 'Temperature_Celsius' in line:
                            # 格式: 194 Temperature_Celsius     0x0022   100   091   000    Old_age   Always       -       35
                            temp = int(line.split()[-1])
                        else:
                            # 格式: Temperature: 35 Celsius
                            temp = int(line.split()[1])
                        smart_info['temperature'] = temp
                    except Exception:
                        pass
            
            return smart_info
            
        except Exception:
            return None
