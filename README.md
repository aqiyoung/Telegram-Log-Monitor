# Telegram Log Monitor

基于Telegram API的日志监控系统，用于从飞牛NAS设备的Debian操作系统中收集关键系统信息并通过Telegram机器人发送。

## 功能特性

- **日志收集**：定期采集系统访问日志、告警日志、硬盘信息和系统性能指标
- **实时监控**：实时监控登录访问事件，并通过Telegram推送通知
- **数据处理**：对收集到的数据进行过滤、格式化和优先级分类
- **Telegram集成**：通过Telegram机器人发送系统信息和告警
- **配置灵活**：支持自定义收集频率、告警阈值和消息格式
- **服务管理**：支持systemd服务自动启动和故障恢复

## 系统要求

- 飞牛NAS设备（Debian操作系统）
- Python 3.6+
- Telegram Bot Token（需要自行创建）
- Telegram用户ID或群组ID（用于接收消息）

## 安装步骤

### 1. 准备Telegram Bot

1. 在Telegram中搜索 `@BotFather` 并开始对话
2. 发送 `/newbot` 命令创建新机器人
3. 按照提示设置机器人名称和用户名
4. 记录生成的Bot Token
5. 创建一个Telegram群组（或使用现有群组），并将机器人添加为管理员
6. 发送 `/start` 命令给机器人，或在群组中发送一条消息，以便机器人获取聊天ID
7. 访问 `https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates` 获取聊天ID

### 2. 安装Telegram Log Monitor

1. 克隆或下载项目到飞牛NAS设备
2. 进入项目目录并运行安装脚本：

```bash
cd telegram-log-monitor
chmod +x install.sh
./install.sh
```

3. 安装脚本会自动：
   - 安装所需依赖包
   - 创建安装目录 `/opt/telegram-log-monitor`
   - 复制项目文件
   - 安装并启动systemd服务

### 3. 配置系统

编辑配置文件 `/opt/telegram-log-monitor/config/config.yaml`，设置以下参数：

```yaml
# Telegram 配置
telegram:
  bot_token: "YOUR_BOT_TOKEN"  # 替换为实际的 Bot Token
  chat_id: "YOUR_CHAT_ID"      # 替换为实际的聊天ID

# 收集器配置（可根据需要调整）
collectors:
  access_log:
    enabled: true
    collect_interval: 3600  # 收集间隔（秒）
  alert_log:
    enabled: true
    collect_interval: 1800  # 收集间隔（秒）
  disk_info:
    enabled: true
    collect_interval: 3600  # 收集间隔（秒）
  system_metrics:
    enabled: true
    collect_interval: 600   # 收集间隔（秒）

# 告警阈值配置（可根据需要调整）
thresholds:
  cpu_usage: 80        # CPU 使用率阈值（%）
  memory_usage: 85     # 内存使用率阈值（%）
  disk_usage: 90       # 磁盘使用率阈值（%）
  disk_temperature: 55  # 磁盘温度阈值（°C）
```

4. 重启服务以应用配置：

```bash
systemctl restart telegram-log-monitor.service
```

## 服务管理

### 启动服务

```bash
systemctl start telegram-log-monitor.service
```

### 停止服务

```bash
systemctl stop telegram-log-monitor.service
```

### 重启服务

```bash
systemctl restart telegram-log-monitor.service
```

### 查看服务状态

```bash
systemctl status telegram-log-monitor.service
```

### 查看服务日志

```bash
journalctl -u telegram-log-monitor.service
```

## 消息格式

系统会发送以下类型的消息：

1. **系统访问日志报告**：记录用户登录、文件访问等操作
2. **系统告警日志报告**：记录错误提示、异常状态等警告信息
3. **硬盘信息报告**：记录容量使用情况、健康状态、温度等SMART数据
4. **系统性能指标报告**：记录CPU使用率、内存占用、网络流量等
5. **每日系统状态报告**：每天8:00发送的综合系统状态报告
6. **实时登录通知**：当检测到登录事件时实时发送的通知

## 实时监控功能

系统支持实时监控登录访问事件，并通过Telegram机器人发送实时通知。当检测到以下登录事件时，系统会立即发送通知：

- **登录成功**：用户成功登录系统
- **登录失败**：用户登录失败（可能是密码错误）
- **无效用户**：尝试使用不存在的用户登录

### 实时监控的实现

1. **依赖**：实时监控功能依赖于`watchdog`库，该库已在`requirements.txt`中列出
2. **自动启用**：当系统启动时，实时监控功能会自动启用（如果`watchdog`库已安装）
3. **通知内容**：实时通知包含登录时间、事件类型、用户名、登录方式和详细信息

### 示例通知

```
🚨 **登录通知**

**时间**: 2026-02-25 15:30:45
**事件**: 登录成功
**用户**: admin
**方式**: password
**详情**: Feb 25 15:30:45 hostname sshd[1234]: Accepted password for admin from 192.168.1.100 port 22 ssh2
```

```
🚨 **安全告警**

**时间**: 2026-02-25 15:31:20
**事件**: 登录失败
**用户**: admin
**详情**: Feb 25 15:31:20 hostname sshd[1235]: Failed password for admin from 192.168.1.100 port 22 ssh2
```

## 故障排除

### 常见问题

1. **服务无法启动**
   - 检查配置文件是否正确
   - 检查Python依赖是否安装
   - 查看服务日志获取详细错误信息

2. **Telegram消息未收到**
   - 检查Bot Token是否正确
   - 检查Chat ID是否正确
   - 检查网络连接是否正常
   - 确保机器人已添加到群组并具有发送消息权限

3. **硬盘信息未收集**
   - 确保已安装smartmontools
   - 检查硬盘是否支持SMART
   - 确保以root用户运行服务

### 日志位置

- 系统日志：`/var/log/syslog`（包含telegram-log-monitor服务日志）
- 应用日志：`/var/log/telegram-log-monitor.log`（可在配置文件中修改）

## 卸载

如需卸载Telegram Log Monitor，运行：

```bash
cd /opt/telegram-log-monitor
./uninstall.sh
```

卸载脚本会自动：
- 停止并禁用服务
- 移除systemd服务文件
- 删除安装目录
- 清理Python依赖

## 安全注意事项

- 保护好你的Bot Token，不要泄露给他人
- 建议只将机器人添加到可信的群组
- 定期检查系统配置，确保收集频率合理，避免过度占用系统资源

## 性能优化

- 根据系统性能调整收集间隔，避免过于频繁的收集
- 对于性能较差的设备，可以禁用一些非必要的收集器
- 调整内存限制，确保服务不会占用过多内存

## 贡献

欢迎提交问题和改进建议！

## 许可证

MIT License
