# 服务器同步系统使用说明

## 功能概述

服务器同步系统实现以下功能：

1. **文件夹共享和数据同步**
   - 自动收集和同步玩家数据
   - 游戏统计数据同步
   - 消息记录同步

2. **定时开关机控制**
   - 中午12点：主服务器同步数据到从服务器，然后关机
   - 凌晨0点：从服务器启动，接收数据，主服务器启动

3. **数据备份**
   - 同步前自动备份
   - 自动清理7天前的备份

## 配置说明

编辑 `sync_config.json` 文件：

```json
{
  "data_dir": "./data",           // 数据存储目录
  "backup_dir": "./backup",       // 备份目录
  "is_primary": false,            // 是否为主服务器（true=主，false=从）
  "sync_port": 9999,              // 同步端口
  "sync_interval": 60,            // 同步间隔（秒）
  "auto_shutdown": true,          // 是否自动关机
  "shutdown_delay": 60,           // 关机延迟（秒）
  "backup_before_sync": true,     // 同步前备份
  "secondary_ip": "192.168.1.100",  // 从服务器IP
  "secondary_mac": "00:11:22:33:44:55", // 从服务器MAC地址（用于WOL）
  "primary_ip": "192.168.1.1",   // 主服务器IP
  "log_level": "INFO",            // 日志级别
  "max_backup_age_days": 7,       // 最大备份保留天数
  "enable_wol": true,             // 是否启用WOL唤醒
  "sync_timeout": 300             // 同步超时（秒）
}
```

## 部署步骤

### 1号机器（主服务器）

1. 设置 `sync_config.json`:
   ```json
   {
     "is_primary": true,
     "primary_ip": "192.168.1.1",
     "secondary_ip": "192.168.1.100"
   }
   ```

2. 运行同步脚本:
   ```bash
   python sync_script.py
   ```

### 2号机器（从服务器）

1. 设置 `sync_config.json`:
   ```json
   {
     "is_primary": false,
     "primary_ip": "192.168.1.1",
     "secondary_ip": "192.168.1.100"
   }
   ```

2. 配置BIOS启用Wake-on-LAN（WOL）

3. 运行同步脚本:
   ```bash
   python sync_script.py
   ```

## 定时任务配置

### 方式一：使用系统定时任务

**Windows (任务计划程序)**:
```cmd
schtasks /create /tn "GameServerSync" /tr "python C:\path\to\sync_script.py" /sc daily /st 00:00
```

**Linux (Cron)**:
```bash
crontab -e
0 0 * * * cd /path/to/Web && python sync_script.py
```

### 方式二：脚本自动运行

脚本会自动检测时间并执行相应的同步操作。

## 工作流程

### 中午12点同步流程

1. **主服务器（1号机器）**
   - 收集玩家数据
   - 备份数据
   - 同步数据到从服务器
   - 等待1分钟
   - 自动关机

2. **从服务器（2号机器）**
   - 接收主服务器数据
   - 应用同步数据
   - 继续运行

### 凌晨0点同步流程

1. **从服务器（2号机器）**
   - 收集玩家数据
   - 备份数据
   - 同步数据到主服务器
   - 等待1分钟
   - 自动关机

2. **主服务器（1号机器）**
   - 启动
   - 等待1分钟
   - 接收从服务器数据
   - 应用同步数据
   - 继续运行

## 数据结构

### 玩家数据格式

```json
{
  "timestamp": "2026-02-13T12:00:00",
  "server_ip": "192.168.1.1",
  "players": {
    "player1": {
      "username": "玩家1",
      "coins": 1000,
      "level": 5,
      "last_login": "2026-02-13T11:30:00"
    }
  },
  "game_stats": {
    "total_players": 10,
    "active_games": 15,
    "total_playtime": 3600
  },
  "messages": [
    {
      "from": "player1",
      "to": "player2",
      "content": "你好",
      "timestamp": "2026-02-13T11:45:00"
    }
  ]
}
```

## 注意事项

1. **网络配置**
   - 确保两台机器在同一局域网
   - 配置静态IP地址
   - 关闭防火墙或开放同步端口

2. **权限设置**
   - 确保脚本有足够的读写权限
   - Windows可能需要管理员权限运行

3. **BIOS设置**
   - 启用Wake-on-LAN功能
   - 配置网络唤醒选项

4. **日志监控**
   - 定期查看 `sync.log` 文件
   - 确保同步操作正常执行

5. **备份管理**
   - 定期检查备份文件
   - 确保有足够的磁盘空间

## 故障排除

### 同步失败

1. 检查网络连接
2. 验证IP地址配置
3. 查看日志文件

### 关机失败

1. 检查脚本权限
2. 确认auto_shutdown设置
3. 验证系统关机命令

### 唤醒失败

1. 确认MAC地址正确
2. 检查BIOS WOL设置
3. 验证网络唤醒功能

## 技术支持

如遇到问题，请检查：
1. 日志文件 `sync.log`
2. 配置文件 `sync_config.json`
3. 网络连接状态
4. 系统权限设置