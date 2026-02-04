# -*- coding: utf-8 -*-
"""
日志系统模块
提供结构化日志输出，支持彩色输出和文件记录
"""
import sys
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""

    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
    }
    RESET = '\033[0m'

    def format(self, record):
        # 添加颜色
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


class AgentLogger:
    """Agent日志记录器"""

    def __init__(self, name: str = "CADAgent", config=None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # 避免重复添加handler
        if self.logger.handlers:
            return

        # 控制台handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)

        # 格式化器
        if config and hasattr(config, 'log') and config.log.colored:
            formatter = ColoredFormatter(
                '%(levelname)s [%(name)s] %(message)s'
            )
        else:
            formatter = logging.Formatter(
                '%(levelname)s [%(name)s] %(message)s'
            )

        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 文件handler（如果配置了）
        if config and hasattr(config, 'log') and config.log.log_file:
            log_file = Path(config.log.log_file)
            log_file.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def debug(self, msg: str):
        self.logger.debug(msg)

    def info(self, msg: str):
        self.logger.info(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def critical(self, msg: str):
        self.logger.critical(msg)

    # 便捷方法
    def step(self, step_num: int, total: int, message: str):
        """输出步骤信息"""
        self.info(f"[{step_num}/{total}] {message}")

    def success(self, msg: str):
        """输出成功信息"""
        self.info(f"✅ {msg}")

    def failure(self, msg: str):
        """输出失败信息"""
        self.error(f"❌ {msg}")

    def progress(self, message: str):
        """输出进度信息"""
        self.info(f"⏳ {message}")

    def result(self, msg: str):
        """输出结果信息"""
        self.info(f"📋 {msg}")


# 全局日志实例
_global_logger: Optional[AgentLogger] = None


def get_logger(name: str = "CADAgent", config=None) -> AgentLogger:
    """获取日志记录器实例"""
    global _global_logger
    if _global_logger is None:
        _global_logger = AgentLogger(name, config)
    return _global_logger


def setup_logger(config=None):
    """设置全局日志记录器"""
    global _global_logger
    _global_logger = AgentLogger("CADAgent", config)
    return _global_logger
