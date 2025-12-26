"""
AI Provider 抽象层

提供统一的 AI Provider 接口，支持：
- OpenAI
- Anthropic Claude
- 本地模型 (Ollama, LM Studio 等)
- 流式响应
- 错误处理和自动重试
"""

import asyncio
import json
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, AsyncIterator, Callable
from dataclasses import dataclass
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProviderType(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    CUSTOM = "custom"


class MessageRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    role: MessageRole
    content: str


@dataclass
class ChatCompletion:
    content: str
    model: str
    usage: Optional[Dict] = None
    raw_response: Optional[Dict] = None


@dataclass
class ProviderConfig:
    type: ProviderType
    api_key: str
    endpoint: Optional[str] = None
    model: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30
    retry_count: int = 3


class AIProvider(ABC):
    """AI Provider 抽象基类"""
    
    @abstractmethod
    async def complete(self, messages: list[Message], stream: bool = False) -> ChatCompletion:
        """发送补全请求"""
        pass
    
    @abstractmethod
    async def stream_complete(self, messages: list[Message]) -> AsyncIterator[str]:
        """流式补全"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """测试连接"""
        pass
    
    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """获取 Provider 类型"""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI Provider"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.base_url = config.endpoint or "https://api.openai.com/v1"
        self.model = config.model or "gpt-3.5-turbo"
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.OPENAI
    
    async def complete(self, messages: list[Message], stream: bool = False) -> ChatCompletion:
        import httpx
        
        formatted_messages = [
            {"role": m.role.value, "content": m.content}
            for m in messages
        ]
        
        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": stream
        }
        
        for attempt in range(self.config.retry_count):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers={"Authorization": f"Bearer {self.config.api_key}"},
                        json=payload,
                        timeout=self.config.timeout
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        content = data["choices"][0]["message"]["content"]
                        usage = data.get("usage", {})
                        return ChatCompletion(
                            content=content,
                            model=self.model,
                            usage=usage,
                            raw_response=data
                        )
                    else:
                        error_data = response.json()
                        error_msg = error_data.get("error", {}).get("message", "Unknown error")
                        
                        if response.status_code == 429:
                            await asyncio.sleep(2 ** attempt)
                            continue
                        
                        raise Exception(f"OpenAI API error: {error_msg}")
                        
            except httpx.TimeoutException:
                if attempt < self.config.retry_count - 1:
                    await asyncio.sleep(1)
                    continue
                raise
        
        raise Exception("Max retries exceeded")
    
    async def stream_complete(self, messages: list[Message]) -> AsyncIterator[str]:
        import httpx
        
        formatted_messages = [
            {"role": m.role.value, "content": m.content}
            for m in messages
        ]
        
        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": True
        }
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.config.api_key}"},
                json=payload,
                timeout=self.config.timeout
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            content = chunk["choices"][0]["delta"].get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            pass
    
    async def test_connection(self) -> bool:
        import httpx
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.config.api_key}"},
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 5
                    },
                    timeout=10
                )
                return response.status_code == 200
        except Exception:
            return False


class AnthropicProvider(AIProvider):
    """Anthropic Claude Provider"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.base_url = config.endpoint or "https://api.anthropic.com"
        self.model = config.model or "claude-sonnet-4-20250514"
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.ANTHROPIC
    
    async def complete(self, messages: list[Message], stream: bool = False) -> ChatCompletion:
        import httpx
        
        formatted_messages = [
            {"role": m.role.value, "content": m.content}
            for m in messages
        ]
        
        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "stream": stream
        }
        
        for attempt in range(self.config.retry_count):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/v1/messages",
                        headers={
                            "Authorization": f"Bearer {self.config.api_key}",
                            "anthropic-version": "2023-06-01"
                        },
                        json=payload,
                        timeout=self.config.timeout
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        content = data["content"][0]["text"]
                        usage = data.get("usage", {})
                        return ChatCompletion(
                            content=content,
                            model=self.model,
                            usage=usage,
                            raw_response=data
                        )
                    else:
                        error_data = response.json()
                        error_msg = error_data.get("error", {}).get("message", "Unknown error")
                        
                        if response.status_code == 429:
                            await asyncio.sleep(2 ** attempt)
                            continue
                        
                        raise Exception(f"Anthropic API error: {error_msg}")
                        
            except httpx.TimeoutException:
                if attempt < self.config.retry_count - 1:
                    await asyncio.sleep(1)
                    continue
                raise
        
        raise Exception("Max retries exceeded")
    
    async def stream_complete(self, messages: list[Message]) -> AsyncIterator[str]:
        import httpx
        
        formatted_messages = [
            {"role": m.role.value, "content": m.content}
            for m in messages
        ]
        
        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "stream": True
        }
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/v1/messages",
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "anthropic-version": "2023-06-01"
                },
                json=payload,
                timeout=self.config.timeout
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            content = chunk["choices"][0]["delta"].get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            pass
    
    async def test_connection(self) -> bool:
        import httpx
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/messages",
                    headers={
                        "Authorization": f"Bearer {self.config.api_key}",
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 5
                    },
                    timeout=10
                )
                return response.status_code == 200
        except Exception:
            return False


class LocalProvider(AIProvider):
    """本地模型 Provider (Ollama, LM Studio 等)"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.base_url = config.endpoint or "http://localhost:11434"
        self.model = config.model or "llama3"
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.LOCAL
    
    async def complete(self, messages: list[Message], stream: bool = False) -> ChatCompletion:
        import httpx
        
        formatted_messages = [
            {"role": m.role.value, "content": m.content}
            for m in messages
        ]
        
        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": stream
        }
        
        for attempt in range(self.config.retry_count):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/v1/chat/completions",
                        json=payload,
                        timeout=self.config.timeout
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        content = data["choices"][0]["message"]["content"]
                        return ChatCompletion(
                            content=content,
                            model=self.model,
                            usage={},
                            raw_response=data
                        )
                    else:
                        raise Exception(f"Local API error: {response.status_code}")
                        
            except httpx.TimeoutException:
                if attempt < self.config.retry_count - 1:
                    await asyncio.sleep(1)
                    continue
                raise
        
        raise Exception("Max retries exceeded")
    
    async def stream_complete(self, messages: list[Message]) -> AsyncIterator[str]:
        import httpx
        
        formatted_messages = [
            {"role": m.role.value, "content": m.content}
            for m in messages
        ]
        
        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": True
        }
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=self.config.timeout
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            content = chunk["choices"][0]["delta"].get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            pass
    
    async def test_connection(self) -> bool:
        import httpx
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 5
                    },
                    timeout=10
                )
                return response.status_code == 200
        except Exception:
            return False


class ProviderManager:
    """Provider 管理器"""
    
    def __init__(self):
        self._providers: Dict[ProviderType, AIProvider] = {}
        self._active_provider: Optional[ProviderType] = None
        self._fallback_provider: Optional[ProviderType] = None
    
    def register_provider(self, provider: AIProvider):
        """注册 Provider"""
        self._providers[provider.provider_type] = provider
    
    def set_active_provider(self, provider_type: ProviderType):
        """设置活动 Provider"""
        if provider_type in self._providers:
            self._active_provider = provider_type
        else:
            raise ValueError(f"Provider {provider_type} not registered")
    
    def set_fallback_provider(self, provider_type: ProviderType):
        """设置备用 Provider"""
        if provider_type in self._providers:
            self._fallback_provider = provider_type
        else:
            raise ValueError(f"Provider {provider_type} not registered")
    
    def get_active_provider(self) -> Optional[AIProvider]:
        """获取活动 Provider"""
        if self._active_provider:
            return self._providers.get(self._active_provider)
        return None
    
    async def complete_with_fallback(
        self, 
        messages: list[Message], 
        stream: bool = False
    ) -> ChatCompletion:
        """使用主 Provider，失败时回退到备用 Provider"""
        active = self.get_active_provider()
        if not active:
            raise ValueError("No active provider configured")
        
        try:
            return await active.complete(messages, stream)
        except Exception as e:
            logger.warning(f"Active provider failed: {e}")
            
            if self._fallback_provider:
                fallback = self._providers.get(self._fallback_provider)
                if fallback:
                    logger.info("Falling back to backup provider")
                    return await fallback.complete(messages, stream)
            
            raise
    
    async def stream_with_fallback(self, messages: list[Message]) -> AsyncIterator[str]:
        """流式请求，带回退"""
        active = self.get_active_provider()
        if not active:
            raise ValueError("No active provider configured")
        
        try:
            async for chunk in active.stream_complete(messages):
                yield chunk
        except Exception as e:
            logger.warning(f"Active provider stream failed: {e}")
            
            if self._fallback_provider:
                fallback = self._providers.get(self._fallback_provider)
                if fallback:
                    logger.info("Falling back to backup provider for streaming")
                    async for chunk in fallback.stream_complete(messages):
                        yield chunk
    
    def list_available_providers(self) -> list[ProviderType]:
        """列出可用的 Providers"""
        return list(self._providers.keys())


def create_provider(config: ProviderConfig) -> AIProvider:
    """工厂方法：创建 Provider"""
    if config.type == ProviderType.OPENAI:
        return OpenAIProvider(config)
    elif config.type == ProviderType.ANTHROPIC:
        return AnthropicProvider(config)
    elif config.type == ProviderType.LOCAL:
        return LocalProvider(config)
    else:
        raise ValueError(f"Unknown provider type: {config.type}")


async def main():
    """测试 Provider"""
    manager = ProviderManager()
    
    openai_config = ProviderConfig(
        type=ProviderType.OPENAI,
        api_key="test-key",
        model="gpt-3.5-turbo"
    )
    manager.register_provider(OpenAIProvider(openai_config))
    manager.set_active_provider(ProviderType.OPENAI)
    
    print(f"Available providers: {manager.list_available_providers()}")
    print(f"Active provider: {manager.get_active_provider().provider_type}")
    
    messages = [Message(role=MessageRole.USER, content="Hello, how are you?")]
    
    try:
        result = await manager.complete_with_fallback(messages)
        print(f"Response: {result.content[:100]}...")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
