# -*- coding: utf-8 -*-
"""
统一的API客户端模块
支持OpenAI兼容的API调用，使用requests库
"""
import json
import time
from typing import Dict, Any, Optional, Tuple
import requests

from .logger import get_logger
from .config import APIConfig


class APIClientError(Exception):
    """API客户端错误"""
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class APIClient:
    """
    统一的API客户端

    支持：
    - 自动重试
    - 模型降级
    - 错误处理
    - 请求/响应日志
    """

    def __init__(self, config: APIConfig):
        """
        初始化API客户端

        Args:
            config: API配置
        """
        self.config = config
        self.logger = get_logger()
        self.session = requests.Session()

        # 设置请求头
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.api_key}",
            "User-Agent": "CADAgent/1.0"
        })

        # 构建API URL
        self.base_url = config.base_url
        if self.base_url.endswith("/chat/completions"):
            self.chat_url = self.base_url
        else:
            self.chat_url = f"{self.base_url}/chat/completions"

    def _send_request(
        self,
        model: str,
        messages: list,
        temperature: float = 0.7,
        max_retries: Optional[int] = None
    ) -> Tuple[Dict[str, Any], str]:
        """
        发送API请求

        Args:
            model: 模型名称
            messages: 消息列表
            temperature: 温度参数
            max_retries: 最大重试次数

        Returns:
            (响应内容, 实际使用的模型)

        Raises:
            APIClientError: API调用失败
        """
        if max_retries is None:
            max_retries = self.config.max_retries

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }

        for attempt in range(max_retries):
            try:
                self.logger.debug(f"发送API请求 (尝试 {attempt + 1}/{max_retries}): {self.chat_url}")

                response = self.session.post(
                    self.chat_url,
                    json=payload,
                    timeout=self.config.timeout
                )

                # 速率限制处理
                if response.status_code == 429:
                    wait_time = 2 * (2 ** attempt)
                    self.logger.warning(f"API速率限制 (429)，等待 {wait_time}s 后重试...")
                    time.sleep(wait_time)
                    continue

                # 其他错误响应
                if response.status_code >= 400:
                    error_msg = response.text
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", {}).get("message", error_msg)
                    except:
                        pass
                    raise APIClientError(
                        f"API返回错误: {error_msg}",
                        status_code=response.status_code,
                        response=error_msg
                    )

                # 成功响应
                data = response.json()
                return data, model

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    self.logger.warning(f"请求超时，{wait_time}s后重试...")
                    time.sleep(wait_time)
                    continue
                raise APIClientError(f"请求超时 (>{self.config.timeout}s)")

            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    self.logger.warning(f"连接错误，{wait_time}s后重试...")
                    time.sleep(wait_time)
                    continue
                raise APIClientError(f"连接失败: {str(e)}")

            except APIClientError:
                raise

            except Exception as e:
                raise APIClientError(f"未知错误: {str(e)}")

        raise APIClientError(f"已达到最大重试次数 ({max_retries})")

    def chat_completion(
        self,
        system_prompt: str,
        user_message: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        enable_fallback: Optional[bool] = None
    ) -> Tuple[str, str]:
        """
        调用聊天补全API

        Args:
            system_prompt: 系统提示词
            user_message: 用户消息
            model: 模型名称（默认使用配置的模型）
            temperature: 温度参数
            enable_fallback: 是否启用降级模型

        Returns:
            (响应内容, 实际使用的模型)

        Raises:
            APIClientError: API调用失败
        """
        if model is None:
            model = self.config.model
        if temperature is None:
            temperature = 0.7
        if enable_fallback is None:
            enable_fallback = self.config.enable_fallback

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        self.logger.debug(f"使用模型: {model}")

        # 尝试主模型
        try:
            data, used_model = self._send_request(model, messages, temperature)
            content = self._extract_content(data)
            return content, used_model
        except APIClientError as e:
            # 如果启用了降级，尝试降级模型
            if enable_fallback and self.config.fallback_model and model != self.config.fallback_model:
                self.logger.warning(f"主模型 {model} 失败，尝试降级到 {self.config.fallback_model}")
                try:
                    data, used_model = self._send_request(self.config.fallback_model, messages, temperature)
                    content = self._extract_content(data)
                    self.logger.info(f"降级成功，使用模型: {used_model}")
                    return content, used_model
                except APIClientError as fallback_error:
                    # 降级也失败，抛出原始错误
                    raise e
            raise

    def _extract_content(self, data: Dict[str, Any]) -> str:
        """从API响应中提取内容"""
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as e:
            raise APIClientError(f"无法解析API响应: {str(e)}")


# 便捷函数
def create_client(config: APIConfig) -> APIClient:
    """创建API客户端实例"""
    return APIClient(config)
