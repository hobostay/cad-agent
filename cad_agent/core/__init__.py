# -*- coding: utf-8 -*-
"""
CAD Agent 核心模块
提供基类、注册机制、异常定义、配置、日志、API客户端和Agent
"""
from .base import PartGenerator, PartSpec
from .registry import (
    GeneratorRegistry,
    register_generator,
    get_generator,
    list_generators,
    get_all_generators,
    create_generator
)
from .exceptions import (
    CADAgentError,
    ValidationError,
    GenerationError,
    RegistrationError,
    StandardPartNotFoundError
)
from .config import (
    Config,
    APIConfig,
    AgentConfig,
    OutputConfig,
    LogConfig,
    get_config,
    set_config
)
from .logger import (
    AgentLogger,
    get_logger,
    setup_logger
)
from .api_client import (
    APIClient,
    APIClientError,
    create_client
)
from .agent import (
    CADAgent,
    AgentResult,
    AgentContext,
    StandardPartDetector,
    SpecGenerator,
    PartGenerator as CorePartGenerator,
    PartValidator,
    MemoryManager,
    run_agent
)

__all__ = [
    # Base classes
    'PartGenerator',
    'PartSpec',
    # Registry
    'GeneratorRegistry',
    'register_generator',
    'get_generator',
    'list_generators',
    'get_all_generators',
    'create_generator',
    # Exceptions
    'CADAgentError',
    'ValidationError',
    'GenerationError',
    'RegistrationError',
    'StandardPartNotFoundError',
    # Config
    'Config',
    'APIConfig',
    'AgentConfig',
    'OutputConfig',
    'LogConfig',
    'get_config',
    'set_config',
    # Logger
    'AgentLogger',
    'get_logger',
    'setup_logger',
    # API Client
    'APIClient',
    'APIClientError',
    'create_client',
    # Agent
    'CADAgent',
    'AgentResult',
    'AgentContext',
    'StandardPartDetector',
    'SpecGenerator',
    'CorePartGenerator',
    'PartValidator',
    'MemoryManager',
    'run_agent',
]
