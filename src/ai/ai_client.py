"""
AI 客户端封装
将 AI 模型相关的函数抽象出来，支持多种 AI 提供商
"""

from typing import Optional
from loguru import logger


class AIClient:
    """AI 客户端封装类"""
    
    def __init__(self, provider: str, api_key: str, model: str, base_url: Optional[str] = None):
        """初始化 AI 客户端
        
        Args:
            provider: AI 提供商 (openai, anthropic, deepseek)
            api_key: API 密钥
            model: 模型名称
            base_url: API 基础 URL (可选)
        """
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.client = None
        
        self._init_client()
    
    def _init_client(self):
        """初始化具体的 AI 客户端"""
        if not self.api_key or self.api_key == "your_ai_api_key_here":
            logger.warning("未配置 AI API Key，AI 功能将不可用")
            return
        
        if self.provider == "openai":
            self._init_openai_client()
        elif self.provider == "anthropic":
            self._init_anthropic_client()
        elif self.provider == "deepseek":
            self._init_deepseek_client()
        else:
            logger.warning(f"未知的 AI 提供商: {self.provider}")
    
    def _init_openai_client(self):
        """初始化 OpenAI 客户端"""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            logger.info("OpenAI 客户端初始化成功")
        except Exception as e:
            logger.error(f"OpenAI 客户端初始化失败: {e}")
            self.client = None
    
    def _init_anthropic_client(self):
        """初始化 Anthropic 客户端"""
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
            logger.info("Anthropic 客户端初始化成功")
        except Exception as e:
            logger.error(f"Anthropic 客户端初始化失败: {e}")
            self.client = None
    
    def _init_deepseek_client(self):
        """初始化 DeepSeek 客户端"""
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url or "https://api.deepseek.com"
            )
            logger.info("DeepSeek 客户端初始化成功")
        except Exception as e:
            logger.error(f"DeepSeek 客户端初始化失败: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """检查 AI 客户端是否可用"""
        return self.client is not None
    
    def generate_completion(self, 
                          system_prompt: str, 
                          user_prompt: str,
                          max_tokens: int = 2000,
                          temperature: float = 0.7) -> Optional[str]:
        """生成 AI 完成内容
        
        Args:
            system_prompt: 系统提示
            user_prompt: 用户提示
            max_tokens: 最大 token 数
            temperature: 温度参数
        
        Returns:
            生成的文本内容，失败返回 None
        """
        if not self.is_available():
            logger.warning("AI 客户端不可用")
            return None
        
        try:
            if self.provider in ["openai", "deepseek"]:
                return self._openai_completion(system_prompt, user_prompt, max_tokens, temperature)
            elif self.provider == "anthropic":
                return self._anthropic_completion(user_prompt, max_tokens, temperature)
            else:
                logger.error(f"不支持的 AI 提供商: {self.provider}")
                return None
        except Exception as e:
            logger.error(f"AI 生成失败: {e}")
            return None
    
    def _openai_completion(self, system_prompt: str, user_prompt: str, 
                          max_tokens: int, temperature: float) -> str:
        """OpenAI/DeepSeek 格式的完成"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def _anthropic_completion(self, user_prompt: str, 
                             max_tokens: int, temperature: float) -> str:
        """Anthropic 格式的完成"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.content[0].text
