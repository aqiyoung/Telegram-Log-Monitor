#!/usr/bin/env python3
"""
配置模块
用于加载和管理系统配置
"""

import os
import yaml

class Config:
    """配置类"""
    
    def __init__(self, config_path):
        """
        初始化配置
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self._config = self._load_config()
        self._parse_config()
    
    def _load_config(self):
        """
        加载配置文件
        
        Returns:
            dict: 配置字典
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _parse_config(self):
        """
        解析配置
        """
        # Telegram 配置
        self.telegram = self._ConfigSection(self._config.get('telegram', {}))
        
        # 收集器配置
        self.collectors = self._ConfigSection(self._config.get('collectors', {}))
        
        # 告警阈值配置
        self.thresholds = self._ConfigSection(self._config.get('thresholds', {}))
        
        # 日志配置
        self.logging = self._ConfigSection(self._config.get('logging', {}))
    
    def reload(self):
        """
        重新加载配置
        """
        self._config = self._load_config()
        self._parse_config()
    
    class _ConfigSection:
        """
        配置节类
        用于将字典转换为对象属性
        """
        
        def __init__(self, data):
            """
            初始化配置节
            
            Args:
                data: 配置数据字典
            """
            for key, value in data.items():
                if isinstance(value, dict):
                    setattr(self, key, self.__class__(value))
                else:
                    setattr(self, key, value)
        
        def __getattr__(self, name):
            """
            获取不存在的属性时返回 None
            
            Args:
                name: 属性名
                
            Returns:
                None
            """
            return None
