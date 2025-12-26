"""
文本处理模块

提供智能文本处理功能：
- 文本纠错
- 文本扩写
- 翻译
- 摘要生成
- 上下文理解
"""

import re
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum
from .providers import AIProvider, Message, MessageRole, ProviderManager, ProviderType, ProviderConfig, create_provider
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextType(Enum):
    EMAIL = "email"
    CHAT = "chat"
    CODE = "code"
    DOCUMENT = "document"
    SOCIAL = "social"
    GENERAL = "general"


class Language(Enum):
    CHINESE = "zh"
    ENGLISH = "en"
    MIXED = "mixed"
    UNKNOWN = "unknown"


@dataclass
class ProcessingResult:
    original_text: str
    processed_text: str
    processing_type: str
    confidence: float
    metadata: Dict = None


@dataclass
class ContextInfo:
    text_type: TextType
    language: Language
    detected_language: str
    has_code: bool
    tone: str
    is_formal: bool


class TextProcessor:
    """文本处理器"""
    
    def __init__(self, provider_manager: ProviderManager = None):
        self.provider_manager = provider_manager or ProviderManager()
        self._setup_default_prompts()
    
    def _setup_default_prompts(self):
        """设置默认提示词"""
        self._prompts = {
            "correction": {
                "zh": "请纠正以下文本中的语法、拼写或标点错误。只返回纠正后的文本，不需要解释：\n\n{text}",
                "en": "Correct any grammar, spelling, or punctuation errors in the following text. Only return the corrected text, no explanations:\n\n{text}"
            },
            "expansion": {
                "default": "Expand the following text by approximately {ratio}x, maintaining the original meaning and style. Only return the expanded text:\n\n{text}"
            },
            "translation": {
                "zh-en": "Translate the following text from Chinese to English. Only return the translated text:\n\n{text}",
                "en-zh": "Translate the following text from English to Chinese. Only return the translated text:\n\n{text}",
                "default": "Translate the following text to {target_lang}. Only return the translated text:\n\n{text}"
            },
            "summarization": {
                "default": "Summarize the following text to approximately {ratio} words, preserving key information:\n\n{text}"
            },
            "context_aware": {
                "formal": "Rewrite the following text with a formal tone:\n\n{text}",
                "casual": "Rewrite the following text with a casual tone:\n\n{text}",
                "professional": "Rewrite the following text with a professional tone:\n\n{text}"
            }
        }
    
    async def correct(
        self, 
        text: str, 
        language: str = "auto"
    ) -> ProcessingResult:
        """文本纠错"""
        lang = self._detect_language(text) if language == "auto" else language
        prompt_template = self._prompts["correction"].get(lang, self._prompts["correction"]["en"])
        prompt = prompt_template.format(text=text)
        
        messages = [Message(role=MessageRole.USER, content=prompt)]
        provider = self.provider_manager.get_active_provider()
        
        if not provider:
            return ProcessingResult(
                original_text=text,
                processed_text="[请先配置 AI 提供商]",
                processing_type="correction",
                confidence=0.0
            )
        
        try:
            result = await provider.complete(messages)
            return ProcessingResult(
                original_text=text,
                processed_text=result.content.strip(),
                processing_type="correction",
                confidence=0.9,
                metadata={"model": result.model, "usage": result.usage}
            )
        except Exception as e:
            logger.error(f"Correction failed: {e}")
            return ProcessingResult(
                original_text=text,
                processed_text=f"[纠错失败: {str(e)}]",
                processing_type="correction",
                confidence=0.0
            )
    
    async def expand(
        self, 
        text: str, 
        ratio: float = 2.0,
        preserve_style: bool = True
    ) -> ProcessingResult:
        """文本扩写"""
        prompt_template = self._prompts["expansion"]["default"]
        prompt = prompt_template.format(ratio=ratio, text=text)
        
        if preserve_style:
            prompt += "\nMaintain the original writing style and tone."
        
        messages = [Message(role=MessageRole.USER, content=prompt)]
        provider = self.provider_manager.get_active_provider()
        
        if not provider:
            return ProcessingResult(
                original_text=text,
                processed_text="[请先配置 AI 提供商]",
                processing_type="expansion",
                confidence=0.0
            )
        
        try:
            result = await provider.complete(messages)
            return ProcessingResult(
                original_text=text,
                processed_text=result.content.strip(),
                processing_type="expansion",
                confidence=0.85,
                metadata={"model": result.model, "ratio": ratio}
            )
        except Exception as e:
            logger.error(f"Expansion failed: {e}")
            return ProcessingResult(
                original_text=text,
                processed_text=f"[扩写失败: {str(e)}]",
                processing_type="expansion",
                confidence=0.0
            )
    
    async def translate(
        self, 
        text: str, 
        direction: str = "zh-en"
    ) -> ProcessingResult:
        """翻译"""
        prompt_template = self._prompts["translation"].get(
            direction, 
            self._prompts["translation"]["default"]
        )
        
        target_lang = "English" if direction == "zh-en" else "Chinese"
        prompt = prompt_template.format(target_lang=target_lang, text=text)
        
        messages = [Message(role=MessageRole.USER, content=prompt)]
        provider = self.provider_manager.get_active_provider()
        
        if not provider:
            return ProcessingResult(
                original_text=text,
                processed_text="[请先配置 AI 提供商]",
                processing_type="translation",
                confidence=0.0
            )
        
        try:
            result = await provider.complete(messages)
            return ProcessingResult(
                original_text=text,
                processed_text=result.content.strip(),
                processing_type="translation",
                confidence=0.9,
                metadata={"direction": direction, "model": result.model}
            )
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return ProcessingResult(
                original_text=text,
                processed_text=f"[翻译失败: {str(e)}]",
                processing_type="translation",
                confidence=0.0
            )
    
    async def summarize(
        self, 
        text: str, 
        target_length: int = 100,
        method: str = "abstractive"
    ) -> ProcessingResult:
        """摘要生成"""
        prompt_template = self._prompts["summarization"]["default"]
        prompt = prompt_template.format(ratio=target_length, text=text)
        
        if method == "extractive":
            prompt += "\nUse extractive summarization, preserving original sentences where possible."
        
        messages = [Message(role=MessageRole.USER, content=prompt)]
        provider = self.provider_manager.get_active_provider()
        
        if not provider:
            return ProcessingResult(
                original_text=text,
                processed_text="[请先配置 AI 提供商]",
                processing_type="summarization",
                confidence=0.0
            )
        
        try:
            result = await provider.complete(messages)
            return ProcessingResult(
                original_text=text,
                processed_text=result.content.strip(),
                processing_type="summarization",
                confidence=0.85,
                metadata={"target_length": target_length, "method": method}
            )
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return ProcessingResult(
                original_text=text,
                processed_text=f"[摘要生成失败: {str(e)}]",
                processing_type="summarization",
                confidence=0.0
            )
    
    def detect_context(self, text: str) -> ContextInfo:
        """检测文本上下文"""
        text_lower = text.lower()
        
        text_type = TextType.GENERAL
        if self._detect_email_context(text_lower):
            text_type = TextType.EMAIL
        elif self._detect_chat_context(text_lower):
            text_type = TextType.CHAT
        elif self._detect_code(text):
            text_type = TextType.CODE
        elif self._detect_social_media(text_lower):
            text_type = TextType.SOCIAL
        
        language = self._detect_language_enum(text)
        
        has_code = self._detect_code(text)
        
        tone = "neutral"
        is_formal = False
        
        formal_indicators = ["dear", "sincerely", "best regards", "respectfully"]
        for indicator in formal_indicators:
            if indicator in text_lower:
                tone = "formal"
                is_formal = True
                break
        
        casual_indicators = ["lol", "hey", "😊", "😄", "brb"]
        for indicator in casual_indicators:
            if indicator in text_lower:
                tone = "casual"
                break
        
        return ContextInfo(
            text_type=text_type,
            language=language,
            detected_language=language.value,
            has_code=has_code,
            tone=tone,
            is_formal=is_formal
        )
    
    def _detect_language(self, text: str) -> str:
        """检测语言"""
        chinese_pattern = re.compile(r'[\u4e00-\u9fa5]')
        english_pattern = re.compile(r'[a-zA-Z]')
        
        has_chinese = bool(chinese_pattern.search(text))
        has_english = bool(english_pattern.search(text))
        
        if has_chinese and has_english:
            return "mixed"
        elif has_chinese:
            return "zh"
        elif has_english:
            return "en"
        return "unknown"
    
    def _detect_language_enum(self, text: str) -> Language:
        """检测语言（返回枚举）"""
        lang = self._detect_language(text)
        if lang == "zh":
            return Language.CHINESE
        elif lang == "en":
            return Language.ENGLISH
        elif lang == "mixed":
            return Language.MIXED
        return Language.UNKNOWN
    
    def _detect_email_context(self, text: str) -> bool:
        """检测邮件上下文"""
        email_patterns = [
            r'dear\s+\w+',
            r'best\s+regards',
            r'sincerely',
            r'\w+@\w+\.\w+',
            r'please\s+find',
        ]
        return any(re.search(p, text) for p in email_patterns)
    
    def _detect_chat_context(self, text: str) -> bool:
        """检测聊天上下文"""
        chat_patterns = [
            r'^hey+\s',
            r'whats?\s+up',
            r'lol',
            r':\)|:\(|:D',
        ]
        return any(re.search(p, text) for p in chat_patterns)
    
    def _detect_code(self, text: str) -> bool:
        """检测代码"""
        code_patterns = [
            r'function\s+\w+',
            r'def\s+\w+',
            r'class\s+\w+',
            r'const\s+\w+',
            r'console\.log',
            r'print\(',
            r'#include',
            r'import\s+.*from',
        ]
        return any(re.search(p, text) for p in code_patterns)
    
    def _detect_social_media(self, text: str) -> bool:
        """检测社交媒体"""
        social_patterns = [
            r'#\w+',
            r'@\w+',
            r'https?://\S+',
        ]
        return any(re.search(p, text) for p in social_patterns)
    
    async def process_with_context(
        self, 
        text: str,
        strategy: str = "auto"
    ) -> Tuple[str, ContextInfo]:
        """根据上下文自动处理文本"""
        context = self.detect_context(text)
        
        if context.has_code:
            return text, context
        
        if strategy == "auto":
            if context.text_type == TextType.EMAIL and context.is_formal:
                strategy = "formal"
            elif context.text_type == TextType.CHAT:
                strategy = "casual"
            else:
                strategy = "correction"
        
        if strategy == "correction":
            result = await self.correct(text, context.language.value)
            return result.processed_text, context
        elif strategy == "formal":
            prompt = self._prompts["context_aware"]["formal"].format(text=text)
            messages = [Message(role=MessageRole.USER, content=prompt)]
            provider = self.provider_manager.get_active_provider()
            if provider:
                completion = await provider.complete(messages)
                return completion.content.strip(), context
        elif strategy == "casual":
            prompt = self._prompts["context_aware"]["casual"].format(text=text)
            messages = [Message(role=MessageRole.USER, content=prompt)]
            provider = self.provider_manager.get_active_provider()
            if provider:
                completion = await provider.complete(messages)
                return completion.content.strip(), context
        
        return text, context


class TextProcessingPipeline:
    """文本处理管道"""
    
    def __init__(self, processor: TextProcessor = None):
        self.processor = processor or TextProcessor()
        self._steps: List[str] = []
    
    def add_step(self, step: str):
        """添加处理步骤"""
        self._steps.append(step)
    
    async def execute(
        self, 
        text: str, 
        context: Optional[Dict] = None
    ) -> List[ProcessingResult]:
        """执行处理管道"""
        results = []
        current_text = text
        
        for step in self._steps:
            if step == "correct":
                result = await self.processor.correct(current_text)
            elif step == "expand":
                result = await self.processor.expand(current_text)
            elif step == "translate":
                result = await self.processor.translate(current_text)
            elif step == "summarize":
                result = await self.processor.summarize(current_text)
            else:
                continue
            
            results.append(result)
            if result.confidence > 0.5:
                current_text = result.processed_text
        
        return results


async def main():
    """测试文本处理"""
    manager = ProviderManager()
    
    openai_config = ProviderConfig(
        type=ProviderType.OPENAI,
        api_key="test-key",
        model="gpt-3.5-turbo"
    )
    manager.register_provider(create_provider(openai_config))
    manager.set_active_provider(ProviderType.OPENAI)
    
    processor = TextProcessor(manager)
    
    test_texts = [
        "I goes to school every day",
        "人工智能正在改变世界",
        "项目使用了 React 和 Node.js",
    ]
    
    for text in test_texts:
        print(f"\nOriginal: {text}")
        
        context = processor.detect_context(text)
        print(f"Context: {context.text_type.value}, {context.language.value}")
        
        result = await processor.correct(text)
        print(f"Corrected: {result.processed_text}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
