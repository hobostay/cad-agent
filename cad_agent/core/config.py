# -*- coding: utf-8 -*-
"""
配置管理模块
使用 Pydantic 进行配置验证和管理
"""
import os
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass, field


@dataclass
class APIConfig:
    """API配置"""
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4"
    timeout: int = 60
    max_retries: int = 3
    # 降级模型配置
    fallback_model: Optional[str] = None
    enable_fallback: bool = True

    def __post_init__(self):
        # 自动移除base_url末尾的斜杠
        self.base_url = self.base_url.rstrip("/")


@dataclass
class AgentConfig:
    """Agent配置"""
    max_iterations: int = 3
    enable_memory: bool = True
    memory_file: str = "agent_memory.json"
    enable_validation: bool = True
    enable_standard_parts: bool = True
    verbose: bool = True

    # 温度参数
    temperature: float = 0.7


@dataclass
class OutputConfig:
    """输出配置"""
    default_dxf: str = "agent_output.dxf"
    default_format: str = "dxf"  # dxf 或 stl
    copy_to_desktop: bool = True
    temp_dir: Optional[str] = None


@dataclass
class LogConfig:
    """日志配置"""
    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    log_file: Optional[str] = "cad_agent.log"
    console_output: bool = True
    colored: bool = True


@dataclass
class Config:
    """主配置类"""
    api: APIConfig
    agent: AgentConfig = field(default_factory=AgentConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    log: LogConfig = field(default_factory=LogConfig)

    @classmethod
    def from_env(cls) -> 'Config':
        """从环境变量加载配置"""
        api_key = os.environ.get("OPENAI_API_KEY", "")
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        model = os.environ.get("OPENAI_MODEL", "glm-4-plus")

        # 智谱API的特殊处理
        if "bigmodel" in base_url:
            fallback_model = "glm-4-flash"
        else:
            fallback_model = None

        api_config = APIConfig(
            api_key=api_key,
            base_url=base_url,
            model=model,
            fallback_model=fallback_model
        )

        return cls(api=api_config)

    @classmethod
    def from_file(cls, config_file: Path) -> 'Config':
        """从配置文件加载"""
        config = {}
        if config_file.exists():
            with open(config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()

        api_config = APIConfig(
            api_key=config.get("OPENAI_API_KEY", ""),
            base_url=config.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            model=config.get("OPENAI_MODEL", "glm-4-plus")
        )

        return cls(api=api_config)

    @classmethod
    def load(cls) -> 'Config':
        """智能加载配置：优先从本地配置文件，其次从环境变量"""
        # 查找配置文件
        project_dir = Path(__file__).parent.parent
        local_config = project_dir / "config.env.local"
        default_config = project_dir / "config.env"

        if local_config.exists():
            return cls.from_file(local_config)
        elif default_config.exists():
            return cls.from_file(default_config)
        else:
            return cls.from_env()

    def validate(self) -> bool:
        """验证配置有效性"""
        if not self.api.api_key:
            raise ValueError("未配置 OPENAI_API_KEY")
        return True


# 全局配置实例
_global_config: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置实例"""
    global _global_config
    if _global_config is None:
        _global_config = Config.load()
    return _global_config


def set_config(config: Config) -> None:
    """设置全局配置"""
    global _global_config
    _global_config = config
