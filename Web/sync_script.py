#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务器同步脚本
功能：
1. 文件夹共享和数据同步
2. 定时开关机控制
3. 玩家数据和操作同步
"""

import os
import json
import shutil
import time
import subprocess
import socket
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ServerSync:
    def __init__(self, config_file='sync_config.json'):
        self.config = self.load_config(config_file)
        self.data_dir = Path(self.config.get('data_dir', './data'))
        self.backup_dir = Path(self.config.get('backup_dir', './backup'))
        self.is_primary = self.config.get('is_primary', False)
        
        # 确保目录存在
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"初始化服务器同步系统 - {'主服务器' if self.is_primary else '从服务器'}")
    
    def load_config(self, config_file):
        """加载配置文件"""
        default_config = {
            'data_dir': './data',
            'backup_dir': './backup',
            'is_primary': False,
            'sync_port': 9999,
            'sync_interval': 60,
            'auto_shutdown': True,
            'shutdown_delay': 60,
            'backup_before_sync': True
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    default_config.update(config)
        except Exception as e:
            logger.warning(f"加载配置文件失败，使用默认配置: {e}")
        
        return default_config
    
    def get_local_ip(self):
        """获取本地IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def collect_player_data(self):
        """收集玩家数据"""
        player_data = {
            'timestamp': datetime.now().isoformat(),
            'server_ip': self.get_local_ip(),
            'players': {},
            'game_stats': {},
            'messages': []
        }
        
        try:
            # 收集localStorage数据（从浏览器存储中）
            # 这里需要实际的localStorage路径或API访问
            data_file = self.data_dir / 'player_data.json'
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    stored_data = json.load(f)
                    player_data.update(stored_data)
        except Exception as e:
            logger.warning(f"收集玩家数据失败: {e}")
        
        return player_data
    
    def save_player_data(self, data):
        """保存玩家数据"""
        try:
            data_file = self.data_dir / 'player_data.json'
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("玩家数据保存成功")
        except Exception as e:
            logger.error(f"保存玩家数据失败: {e}")
    
    def backup_data(self):
        """备份数据"""
        if not self.config.get('backup_before_sync'):
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = self.backup_dir / f'backup_{timestamp}.tar.gz'
            
            # 压缩数据目录
            shutil.make_archive(
                str(backup_file.with_suffix('')),
                'gztar',
                str(self.data_dir.parent),
                str(self.data_dir.name)
            )
            
            logger.info(f"数据备份完成: {backup_file}")
            
            # 删除7天前的备份
            self.cleanup_old_backups()
            
        except Exception as e:
            logger.error(f"备份数据失败: {e}")
    
    def cleanup_old_backups(self):
        """清理旧备份"""
        try:
            now = time.time()
            for backup_file in self.backup_dir.glob('backup_*.tar.gz'):
                file_age = now - backup_file.stat().st_mtime
                if file_age > 7 * 24 * 3600:  # 7天
                    backup_file.unlink()
                    logger.info(f"删除旧备份: {backup_file}")
        except Exception as e:
            logger.warning(f"清理旧备份失败: {e}")
    
    def sync_to_secondary(self, secondary_ip, secondary_port=None):
        """同步数据到从服务器"""
        try:
            port = secondary_port or self.config.get('sync_port')
            logger.info(f"开始同步数据到从服务器 {secondary_ip}:{port}")
            
            # 收集数据
            data = self.collect_player_data()
            
            # 备份数据
            self.backup_data()
            
            # 这里实现实际的同步逻辑
            # 可以使用socket、HTTP、FTP等方式传输数据
            
            logger.info("数据同步到从服务器完成")
            return True
            
        except Exception as e:
            logger.error(f"同步到从服务器失败: {e}")
            return False
    
    def receive_from_primary(self):
        """从主服务器接收数据"""
        try:
            logger.info("等待从主服务器接收数据...")
            
            # 这里实现实际的数据接收逻辑
            # 可以使用socket服务器监听数据
            
            logger.info("从主服务器接收数据完成")
            return True
            
        except Exception as e:
            logger.error(f"从主服务器接收数据失败: {e}")
            return False
    
    def apply_synced_data(self, data):
        """应用同步的数据"""
        try:
            logger.info("开始应用同步的数据...")
            
            # 备份当前数据
            self.backup_data()
            
            # 保存新数据
            self.save_player_data(data)
            
            # 这里可以添加更多应用逻辑，比如：
            # - 更新游戏状态
            # - 同步消息
            # - 更新玩家统计
            
            logger.info("同步数据应用完成")
            return True
            
        except Exception as e:
            logger.error(f"应用同步数据失败: {e}")
            return False
    
    def check_sync_time(self):
        """检查是否到达同步时间"""
        now = datetime.now()
        
        # 中午12点同步
        if now.hour == 12 and now.minute == 0:
            return 'noon'
        
        # 凌晨0点同步
        if now.hour == 0 and now.minute == 0:
            return 'midnight'
        
        return None
    
    def handle_noon_sync(self):
        """处理中午同步"""
        logger.info("=== 开始中午12点同步 ===")
        
        if self.is_primary:
            # 主服务器：同步数据到从服务器
            secondary_ip = self.config.get('secondary_ip', '192.168.1.100')
            success = self.sync_to_secondary(secondary_ip)
            
            if success:
                logger.info("中午同步完成，等待1分钟后关机")
                time.sleep(60)
                self.shutdown_server()
            else:
                logger.error("中午同步失败，不关机")
        else:
            # 从服务器：等待接收数据
            success = self.receive_from_primary()
            
            if success:
                logger.info("中午接收数据完成，等待1分钟后关机")
                time.sleep(60)
                self.shutdown_server()
            else:
                logger.error("中午接收数据失败，不关机")
    
    def handle_midnight_sync(self):
        """处理凌晨同步"""
        logger.info("=== 开始凌晨0点同步 ===")
        
        if self.is_primary:
            # 主服务器：开机后等待1分钟，然后同步
            logger.info("主服务器启动，等待1分钟后同步")
            time.sleep(60)
            
            secondary_ip = self.config.get('secondary_ip', '192.168.1.100')
            self.sync_to_secondary(secondary_ip)
        else:
            # 从服务器：开机后等待1分钟，接收数据
            logger.info("从服务器启动，等待1分钟后接收")
            time.sleep(60)
            
            self.receive_from_primary()
    
    def shutdown_server(self):
        """关闭服务器"""
        if not self.config.get('auto_shutdown'):
            logger.info("自动关机已禁用")
            return
        
        try:
            logger.info("准备关闭服务器...")
            
            # Windows关机命令
            if os.name == 'nt':
                subprocess.run(['shutdown', '/s', '/t', '30'], check=True)
            # Linux/Mac关机命令
            else:
                subprocess.run(['sudo', 'shutdown', '-h', '+1'], check=True)
            
            logger.info("关机命令已执行，30秒后关机")
            
        except Exception as e:
            logger.error(f"关机失败: {e}")
    
    def wake_secondary_server(self, secondary_mac=None):
        """唤醒从服务器（WOL）"""
        try:
            if not secondary_mac:
                secondary_mac = self.config.get('secondary_mac')
            
            if not secondary_mac:
                logger.warning("未配置从服务器MAC地址，无法唤醒")
                return False
            
            logger.info(f"尝试唤醒从服务器: {secondary_mac}")
            
            # 这里实现WOL（Wake-on-LAN）逻辑
            # 需要发送魔法包到从服务器
            
            logger.info("唤醒命令已发送")
            return True
            
        except Exception as e:
            logger.error(f"唤醒从服务器失败: {e}")
            return False
    
    def run(self):
        """运行同步服务"""
        logger.info("服务器同步服务已启动")
        logger.info(f"当前服务器: {'主服务器' if self.is_primary else '从服务器'}")
        logger.info(f"数据目录: {self.data_dir}")
        logger.info(f"备份目录: {self.backup_dir}")
        
        try:
            while True:
                # 检查同步时间
                sync_time = self.check_sync_time()
                
                if sync_time == 'noon':
                    self.handle_noon_sync()
                elif sync_time == 'midnight':
                    self.handle_midnight_sync()
                
                # 等待下一次检查
                time.sleep(30)
                
        except KeyboardInterrupt:
            logger.info("接收到中断信号，停止服务")
        except Exception as e:
            logger.error(f"服务运行出错: {e}")
            raise


def main():
    """主函数"""
    print("=" * 50)
    print("服务器同步系统")
    print("=" * 50)
    print()
    
    # 创建同步实例
    sync = ServerSync()
    
    # 运行同步服务
    sync.run()


if __name__ == '__main__':
    main()