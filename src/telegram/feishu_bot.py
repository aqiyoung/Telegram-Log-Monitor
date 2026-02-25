#!/usr/bin/env python3
"""
飞书集成模块
用于通过飞书机器人发送处理后的系统信息
"""

import time
import logging
import requests
from requests.exceptions import RequestException

class FeishuBot:
    """飞书机器人"""
    
    def __init__(self, config):
        """
        初始化飞书机器人
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.webhook_url = config.feishu.webhook_url
        self.retry_attempts = config.feishu.retry_attempts
        self.retry_delay = config.feishu.retry_delay
    
    def send_message(self, message):
        """
        发送消息到飞书
        
        Args:
            message: 消息内容
            
        Returns:
            bool: 发送是否成功
        """
        # 构建消息体
        payload = {
            "msg_type": "text",
            "content": {
                "text": message
            }
        }
        
        # 发送消息，支持重试
        for attempt in range(self.retry_attempts):
            try:
                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    timeout=10
                )
                
                # 检查响应
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data.get('code') == 0:
                        logging.info(f"飞书消息发送成功")
                        return True
                    else:
                        logging.error(f"飞书消息发送失败: {response_data.get('code')}, {response_data.get('msg')}")
                else:
                    logging.error(f"飞书消息发送失败: {response.status_code}, {response.text}")
                    
            except RequestException as e:
                logging.error(f"飞书消息发送异常: {e}")
            
            # 重试延迟
            if attempt < self.retry_attempts - 1:
                logging.info(f"将在 {self.retry_delay} 秒后重试")
                time.sleep(self.retry_delay)
        
        logging.error(f"飞书消息发送失败，已达到最大重试次数")
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
                    
                    # 避免消息发送过快
                    time.sleep(1)
        
        return status
    
    def test_connection(self):
        """
        测试飞书连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            # 发送测试消息
            test_message = "飞书机器人连接测试"
            return self.send_message(test_message)
        except Exception as e:
            logging.error(f"飞书机器人连接测试异常: {e}")
            return False
