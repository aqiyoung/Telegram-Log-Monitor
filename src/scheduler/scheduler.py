#!/usr/bin/env python3
"""
调度器模块
用于根据配置的时间间隔执行各个收集器的收集任务
"""

import time
import threading
import logging
import schedule

class Scheduler:
    """调度器"""
    
    def __init__(self, config, collector_manager, processor_manager, telegram_bot, logger):
        """
        初始化调度器
        
        Args:
            config: 配置对象
            collector_manager: 收集器管理器
            processor_manager: 处理器管理器
            telegram_bot: Telegram 机器人
            logger: 日志记录器
        """
        self.config = config
        self.collector_manager = collector_manager
        self.processor_manager = processor_manager
        self.telegram_bot = telegram_bot
        self.logger = logger
        self.running = False
        self.schedule_thread = None
    
    def start(self):
        """
        启动调度器
        """
        self.logger.info('启动调度器')
        self.running = True
        
        # 初始化调度任务
        self._setup_schedules()
        
        # 启动调度线程
        self.schedule_thread = threading.Thread(target=self._run_schedule, daemon=True)
        self.schedule_thread.start()
        
        # 发送启动通知
        self.telegram_bot.send_alert("Telegram Log Monitor 已启动", severity="info")
    
    def stop(self):
        """
        停止调度器
        """
        self.logger.info('停止调度器')
        self.running = False
        
        # 等待调度线程结束
        if self.schedule_thread:
            self.schedule_thread.join(timeout=5)
        
        # 停止实时监控
        if self.collector_manager:
            self.collector_manager.stop_real_time_monitoring()
        
        # 发送停止通知
        self.telegram_bot.send_alert("Telegram Log Monitor 已停止", severity="info")
    
    def _setup_schedules(self):
        """
        设置调度任务
        """
        # 系统访问日志收集
        if self.config.collectors.access_log and self.config.collectors.access_log.enabled:
            interval = self.config.collectors.access_log.collect_interval
            schedule.every(interval).seconds.do(self._collect_and_process, 'access_log')
            self.logger.info(f"设置访问日志收集任务，间隔 {interval} 秒")
        
        # 系统告警日志收集
        if self.config.collectors.alert_log and self.config.collectors.alert_log.enabled:
            interval = self.config.collectors.alert_log.collect_interval
            schedule.every(interval).seconds.do(self._collect_and_process, 'alert_log')
            self.logger.info(f"设置告警日志收集任务，间隔 {interval} 秒")
        
        # 硬盘信息收集
        if self.config.collectors.disk_info and self.config.collectors.disk_info.enabled:
            interval = self.config.collectors.disk_info.collect_interval
            schedule.every(interval).seconds.do(self._collect_and_process, 'disk_info')
            self.logger.info(f"设置硬盘信息收集任务，间隔 {interval} 秒")
        
        # 系统性能指标收集
        if self.config.collectors.system_metrics and self.config.collectors.system_metrics.enabled:
            interval = self.config.collectors.system_metrics.collect_interval
            schedule.every(interval).seconds.do(self._collect_and_process, 'system_metrics')
            self.logger.info(f"设置系统性能指标收集任务，间隔 {interval} 秒")
        
        # 每日系统状态报告
        schedule.every().day.at("08:00").do(self._send_daily_report)
        self.logger.info("设置每日系统状态报告任务，时间 08:00")
    
    def _run_schedule(self):
        """
        运行调度任务
        """
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"调度器运行异常: {e}")
                time.sleep(5)
    
    def _collect_and_process(self, collector_name):
        """
        执行收集和处理任务
        
        Args:
            collector_name: 收集器名称
        """
        try:
            self.logger.info(f"开始收集 {collector_name} 数据")
            
            # 执行收集
            data = self.collector_manager.collect(collector_name)
            
            if data and data.get('status') == 'success':
                # 执行处理
                processed_data = self.processor_manager.process(collector_name, data)
                
                if processed_data and processed_data.get('status') == 'success':
                    # 发送消息
                    self._send_collector_report(collector_name, processed_data)
                    
                    # 检查是否需要发送告警
                    self._check_and_send_alerts(collector_name, processed_data)
            
            self.logger.info(f"完成收集 {collector_name} 数据")
            
        except Exception as e:
            self.logger.error(f"执行 {collector_name} 收集任务异常: {e}")
            # 发送错误通知
            self.telegram_bot.send_alert(f"执行 {collector_name} 收集任务时发生错误: {e}", severity="error")
    
    def _send_collector_report(self, collector_name, processed_data):
        """
        发送收集器报告
        
        Args:
            collector_name: 收集器名称
            processed_data: 处理后的数据
        """
        message = processed_data.get('formatted_message')
        if message:
            # 构建报告名称
            report_names = {
                'access_log': "系统访问日志报告",
                'alert_log': "系统告警日志报告",
                'disk_info': "硬盘信息报告",
                'system_metrics': "系统性能指标报告"
            }
            
            report_name = report_names.get(collector_name, "系统报告")
            full_message = f"📋 {report_name}\n\n{message}"
            
            # 发送消息
            self.telegram_bot.send_message(full_message)
    
    def _check_and_send_alerts(self, collector_name, processed_data):
        """
        检查并发送告警
        
        Args:
            collector_name: 收集器名称
            processed_data: 处理后的数据
        """
        # 根据收集器类型检查告警
        if collector_name == 'system_metrics':
            # 检查系统性能指标告警
            self._check_system_metrics_alerts(processed_data)
        elif collector_name == 'disk_info':
            # 检查硬盘信息告警
            self._check_disk_info_alerts(processed_data)
    
    def _check_system_metrics_alerts(self, processed_data):
        """
        检查系统性能指标告警
        
        Args:
            processed_data: 处理后的数据
        """
        metrics = processed_data.get('prioritized_metrics', {})
        
        # 检查高优先级指标
        for metric in metrics.get('high', []):
            self.telegram_bot.send_alert(metric.get('message'), severity="critical")
        
        # 检查中优先级指标
        for metric in metrics.get('medium', []):
            self.telegram_bot.send_alert(metric.get('message'), severity="warning")
    
    def _check_disk_info_alerts(self, processed_data):
        """
        检查硬盘信息告警
        
        Args:
            processed_data: 处理后的数据
        """
        # 检查磁盘使用情况告警
        usage = processed_data.get('prioritized_usage', {})
        for disk in usage.get('high', []):
            alert_message = f"磁盘 {disk.get('device')} 使用率过高: {disk.get('percent', 0):.1f}%"
            self.telegram_bot.send_alert(alert_message, severity="critical")
        
        for disk in usage.get('medium', []):
            alert_message = f"磁盘 {disk.get('device')} 使用率较高: {disk.get('percent', 0):.1f}%"
            self.telegram_bot.send_alert(alert_message, severity="warning")
        
        # 检查磁盘健康状态告警
        health = processed_data.get('prioritized_health', {})
        for disk in health.get('high', []):
            status = disk.get('status', '未知')
            temperature = disk.get('temperature')
            temp_str = f"，温度: {temperature}°C" if temperature else ""
            alert_message = f"磁盘 {disk.get('device')} 状态异常: {status}{temp_str}"
            self.telegram_bot.send_alert(alert_message, severity="critical")
        
        for disk in health.get('medium', []):
            status = disk.get('status', '未知')
            temperature = disk.get('temperature')
            temp_str = f"，温度: {temperature}°C" if temperature else ""
            alert_message = f"磁盘 {disk.get('device')} 状态需要关注: {status}{temp_str}"
            self.telegram_bot.send_alert(alert_message, severity="warning")
    
    def _send_daily_report(self):
        """
        发送每日系统状态报告
        """
        try:
            self.logger.info("发送每日系统状态报告")
            
            # 收集所有数据
            all_data = self.collector_manager.collect_all()
            
            # 处理所有数据
            processed_data = self.processor_manager.process_all(all_data)
            
            # 发送系统报告
            self.telegram_bot.send_system_report(processed_data)
            
        except Exception as e:
            self.logger.error(f"发送每日系统状态报告异常: {e}")
            # 发送错误通知
            self.telegram_bot.send_alert(f"发送每日系统状态报告时发生错误: {e}", severity="error")
