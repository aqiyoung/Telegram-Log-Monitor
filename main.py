#!/usr/bin/env python3
"""
Telegram Log Monitor 主脚本
用于从飞牛NAS设备的Debian系统中收集关键系统信息并通过Telegram机器人发送
"""

import os
import sys
import time
import logging
from logging.handlers import RotatingFileHandler

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.config import Config
from collectors.collector_manager import CollectorManager
from processors.processor_manager import ProcessorManager
from telegram.telegram_bot import TelegramBot
from scheduler.scheduler import Scheduler

def setup_logging(config):
    """设置日志配置"""
    log_level = getattr(logging, config.logging.level.upper(), logging.INFO)
    log_file = config.logging.log_file
    
    # 确保日志目录存在
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 配置日志
    logger = logging.getLogger('telegram-log-monitor')
    logger.setLevel(log_level)
    
    # 文件处理器
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # 格式化器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def main():
    """主函数"""
    try:
        # 加载配置
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.yaml')
        config = Config(config_path)
        
        # 设置日志
        logger = setup_logging(config)
        logger.info('Telegram Log Monitor 启动')
        
        # 初始化 Telegram Bot
        telegram_bot = TelegramBot(config)
        
        # 初始化收集器管理器（传入 Telegram Bot 实例用于实时推送）
        collector_manager = CollectorManager(config, telegram_bot)
        
        # 初始化处理器管理器
        processor_manager = ProcessorManager(config)
        
        # 初始化调度器
        scheduler = Scheduler(config, collector_manager, processor_manager, telegram_bot, logger)
        
        # 启动调度器
        scheduler.start()
        
        # 主循环
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info('收到停止信号，正在关闭...')
            scheduler.stop()
            logger.info('Telegram Log Monitor 已关闭')
            
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
