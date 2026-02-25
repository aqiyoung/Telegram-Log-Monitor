#!/usr/bin/env python3
"""
Telegram 集成模块
用于通过 Telegram 机器人发送处理后的系统信息
"""

import time
import logging
import requests
from requests.exceptions import RequestException

class TelegramBot:
    """Telegram 机器人"""
    
    def __init__(self, config):
        """
        初始化 Telegram 机器人
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.bot_token = config.telegram.bot_token
        self.chat_id = config.telegram.chat_id
        self.message_format = config.telegram.message_format
        self.retry_attempts = config.telegram.retry_attempts
        self.retry_delay = config.telegram.retry_delay
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/"
    
    def send_message(self, message, parse_mode=None):
        """
        发送消息到 Telegram
        
        Args:
            message: 消息内容
            parse_mode: 解析模式，默认为配置中的格式
            
        Returns:
            bool: 发送是否成功
        """
        if not parse_mode:
            parse_mode = self.message_format
        
        # 消息参数
        params = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': parse_mode
        }
        
        # 发送消息，支持重试
        for attempt in range(self.retry_attempts):
            try:
                response = requests.post(
                    f"{self.api_url}sendMessage",
                    json=params,
                    timeout=10
                )
                
                # 检查响应
                if response.status_code == 200:
                    logging.info(f"Telegram 消息发送成功")
                    return True
                else:
                    logging.error(f"Telegram 消息发送失败: {response.status_code}, {response.text}")
                    
            except RequestException as e:
                logging.error(f"Telegram 消息发送异常: {e}")
            
            # 重试延迟
            if attempt < self.retry_attempts - 1:
                logging.info(f"将在 {self.retry_delay} 秒后重试")
                time.sleep(self.retry_delay)
        
        logging.error(f"Telegram 消息发送失败，已达到最大重试次数")
        return False
    
    def send_alert(self, alert_message, severity="warning"):
        """
        发送告警消息
        
        Args:
            alert_message: 告警消息内容
            severity: 告警级别 (info, warning, error, critical)
            
        Returns:
            bool: 发送是否成功
        """
        # 根据告警级别添加前缀
        severity_prefixes = {
            'info': "ℹ️ 信息",
            'warning': "⚠️ 警告",
            'error': "❌ 错误",
            'critical': "🚨 严重"
        }
        
        prefix = severity_prefixes.get(severity, "ℹ️ 信息")
        formatted_message = f"{prefix}\n\n{alert_message}"
        
        return self.send_message(formatted_message)
    
    def send_system_report(self, reports):
        """
        发送系统报告
        
        Args:
            reports: 系统报告字典，包含各个模块的报告
            
        Returns:
            dict: 各报告发送状态
        """
        status = {}
        
        for report_name, report_data in reports.items():
            if report_data and report_data.get('status') == 'success':
                message = report_data.get('formatted_message')
                if message:
                    # 添加报告标题
                    report_titles = {
                        'access_log': "📊 系统访问日志报告",
                        'alert_log': "🚨 系统告警日志报告",
                        'disk_info': "💾 硬盘信息报告",
                        'system_metrics': "⚡ 系统性能指标报告"
                    }
                    
                    title = report_titles.get(report_name, "📋 系统报告")
                    full_message = f"{title}\n\n{message}"
                    
                    # 发送消息
                    sent = self.send_message(full_message)
                    status[report_name] = sent
                    
                    # 避免消息发送过快被 Telegram API 限制
                    time.sleep(1)
        
        return status
    
    def test_connection(self):
        """
        测试 Telegram 连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            # 获取机器人信息
            response = requests.get(f"{self.api_url}getMe", timeout=10)
            
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get('ok'):
                    logging.info(f"Telegram 机器人连接成功: {bot_info.get('result', {}).get('username')}")
                    return True
                else:
                    logging.error(f"Telegram 机器人连接失败: {bot_info.get('description')}")
            else:
                logging.error(f"Telegram 机器人连接失败: {response.status_code}")
                
        except RequestException as e:
            logging.error(f"Telegram 机器人连接异常: {e}")
        
        return False
    
    def get_chat_id(self, username=None):
        """
        获取聊天 ID
        
        Args:
            username: 用户名（可选）
            
        Returns:
            str: 聊天 ID
        """
        # 如果已经配置了聊天 ID，直接返回
        if self.chat_id:
            return self.chat_id
        
        # 否则尝试通过用户名获取
        if username:
            try:
                response = requests.get(
                    f"{self.api_url}getChat",
                    params={'chat_id': f"@{username}"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    chat_info = response.json()
                    if chat_info.get('ok'):
                        chat_id = chat_info.get('result', {}).get('id')
                        logging.info(f"获取聊天 ID 成功: {chat_id}")
                        return str(chat_id)
            except RequestException as e:
                logging.error(f"获取聊天 ID 异常: {e}")
        
        return None
