"""
策略引擎模块

实现智能文本处理的策略匹配和调度，支持：
- 基于上下文的策略匹配
- 用户偏好集成
- 策略链式调用
- 性能优化
"""

import re
from typing import Optional, Dict, Any, List, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import hashlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StrategyType(Enum):
    CORRECTION = "correction"
    EXPANSION = "expansion"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    COMPLETION = "completion"
    CUSTOM = "custom"


class StrategyPriority(Enum):
    LOW = 1
    MEDIUM = 5
    HIGH = 10
    CRITICAL = 100


@dataclass
class StrategyMatch:
    strategy_type: StrategyType
    confidence: float
    matched_patterns: List[str]
    priority: StrategyPriority
    metadata: Dict = field(default_factory=dict)


@dataclass
class StrategyConfig:
    enabled: bool = True
    priority: StrategyPriority = StrategyPriority.MEDIUM
    min_confidence: float = 0.5
    parameters: Dict = field(default_factory=dict)


@dataclass
class UserPreferences:
    preferred_language: str = "zh"
    correction_enabled: bool = True
    expansion_enabled: bool = True
    translation_enabled: bool = True
    summarization_enabled: bool = True
    auto_expand_shortcuts: bool = True
    strategy_priorities: Dict[StrategyType, int] = field(default_factory=dict)
    learned_preferences: Dict[str, float] = field(default_factory=dict)


class PatternMatcher:
    """模式匹配器"""
    
    def __init__(self):
        self._patterns: Dict[str, re.Pattern] = {}
        self._custom_patterns: List[Tuple[re.Pattern, str]] = []
    
    def add_pattern(self, name: str, pattern: str):
        """添加模式"""
        self._patterns[name] = re.compile(pattern)
    
    def add_custom_pattern(self, pattern: str, strategy_type: str):
        """添加自定义模式"""
        self._custom_patterns.append((re.compile(pattern), strategy_type))
    
    def detect_language(self, text: str) -> str:
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
    
    def detect_typos(self, text: str) -> bool:
        """检测拼写错误"""
        common_typos = [
            r'\bteh\b', r'\btaht\b', r'\bwrok\b', r'\btaht\b',
            r'\brecieved\b', r'\boccured\b', r'\bseperate\b',
            r'\bdefinately\b', r'\baccomodate\b'
        ]
        for pattern in common_typos:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def detect_expansion_candidate(self, text: str) -> bool:
        """检测是否可能是扩写候选"""
        short_patterns = [
            r'^.{1,10}$',
            r'\b(AI|API|SDK|URL|HTTP|TCP|UDP)\b',
        ]
        for pattern in short_patterns:
            if re.match(pattern, text):
                return True
        return False
    
    def detect_translation_candidate(self, text: str) -> Tuple[bool, str]:
        """检测是否可能是翻译候选"""
        mixed_pattern = r'^[\u4e00-\u9fa5]+ [a-zA-Z]+$|^[a-zA-Z]+ [\u4e00-\u9fa5]+$'
        if re.match(mixed_pattern, text):
            return True, "mixed"
        
        has_chinese = bool(re.search(r'[\u4e00-\u9fa5]', text))
        has_english = bool(re.search(r'[a-zA-Z]', text))
        
        if has_chinese and not has_english:
            return True, "zh-en"
        elif has_english and not has_chinese:
            return True, "en-zh"
        
        return False, ""
    
    def detect_email_context(self, text: str) -> bool:
        """检测邮件上下文"""
        email_patterns = [
            r'dear\s+\w+',
            r'best\s+regards',
            r'sincerely',
            r'\w+@\w+\.\w+',
            r'please\s+find',
        ]
        for pattern in email_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def detect_chat_context(self, text: str) -> bool:
        """检测聊天上下文"""
        chat_patterns = [
            r'LOL',
            r':\)|:\(|:D',
            r'hey+\s+\w*',
            r'whats?\s+up',
            r'brb',
            r'ttyl',
        ]
        for pattern in chat_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def detect_code(self, text: str) -> bool:
        """检测代码内容"""
        code_patterns = [
            r'function\s+\w+',
            r'def\s+\w+',
            r'class\s+\w+',
            r'const\s+\w+',
            r'let\s+\w+',
            r'var\s+\w+',
            r'import\s+.*from',
            r'#include',
            r'console\.log',
            r'print\(',
        ]
        for pattern in code_patterns:
            if re.search(pattern, text):
                return True
        return False


class StrategyMatcher:
    """策略匹配器"""
    
    def __init__(self, pattern_matcher: Optional[PatternMatcher] = None):
        self.pattern_matcher = pattern_matcher or PatternMatcher()
        self._match_cache: Dict[str, List[StrategyMatch]] = {}
        self._cache_size = 1000
    
    def match_strategies(
        self, 
        text: str, 
        context: Optional[Dict] = None,
        preferences: Optional[UserPreferences] = None
    ) -> List[StrategyMatch]:
        """匹配适用的策略"""
        cache_key = self._generate_cache_key(text, context)
        
        if cache_key in self._match_cache:
            matches = self._match_cache[cache_key]
            if preferences:
                matches = self._apply_preferences(matches, preferences)
            return matches
        
        matches = []
        
        if self.pattern_matcher.detect_code(text):
            matches.append(StrategyMatch(
                strategy_type=StrategyType.CUSTOM,
                confidence=0.99,
                matched_patterns=["code_detected"],
                priority=StrategyPriority.CRITICAL,
                metadata={"action": "protect_code"}
            ))
            return self._finalize_matches(matches, cache_key, preferences)
        
        if self.pattern_matcher.detect_typos(text):
            matches.append(StrategyMatch(
                strategy_type=StrategyType.CORRECTION,
                confidence=0.95,
                matched_patterns=["typo_detected"],
                priority=StrategyPriority.HIGH
            ))
        
        is_translation, direction = self.pattern_matcher.detect_translation_candidate(text)
        if is_translation and (preferences and preferences.translation_enabled):
            matches.append(StrategyMatch(
                strategy_type=StrategyType.TRANSLATION,
                confidence=0.85,
                matched_patterns=["translation_candidate"],
                priority=StrategyPriority.MEDIUM,
                metadata={"direction": direction}
            ))
        
        if self.pattern_matcher.detect_expansion_candidate(text) and (preferences and preferences.expansion_enabled):
            matches.append(StrategyMatch(
                strategy_type=StrategyType.EXPANSION,
                confidence=0.75,
                matched_patterns=["short_text", "expansion_candidate"],
                priority=StrategyPriority.MEDIUM
            ))
        
        if self.pattern_matcher.detect_email_context(text):
            matches.append(StrategyMatch(
                strategy_type=StrategyType.CUSTOM,
                confidence=0.8,
                matched_patterns=["email_context"],
                priority=StrategyPriority.LOW,
                metadata={"action": "formal_tone"}
            ))
        
        if self.pattern_matcher.detect_chat_context(text):
            matches.append(StrategyMatch(
                strategy_type=StrategyType.CUSTOM,
                confidence=0.8,
                matched_patterns=["chat_context"],
                priority=StrategyPriority.LOW,
                metadata={"action": "casual_tone"}
            ))
        
        return self._finalize_matches(matches, cache_key, preferences)
    
    def _generate_cache_key(self, text: str, context: Optional[Dict]) -> str:
        """生成缓存键"""
        content = text[:100]
        if context:
            content += str(sorted(context.items()))
        return hashlib.md5(content.encode()).hexdigest()
    
    def _apply_preferences(
        self, 
        matches: List[StrategyMatch],
        preferences: UserPreferences
    ) -> List[StrategyMatch]:
        """应用用户偏好"""
        result = []
        for match in matches:
            if match.strategy_type == StrategyType.CORRECTION and not preferences.correction_enabled:
                continue
            if match.strategy_type == StrategyType.EXPANSION and not preferences.expansion_enabled:
                continue
            if match.strategy_type == StrategyType.TRANSLATION and not preferences.translation_enabled:
                continue
            if match.strategy_type == StrategyType.SUMMARIZATION and not preferences.summarization_enabled:
                continue
            
            priority_override = preferences.strategy_priorities.get(match.strategy_type)
            if priority_override:
                match.priority = StrategyPriority(priority_override)
            
            result.append(match)
        
        return result
    
    def _finalize_matches(
        self, 
        matches: List[StrategyMatch],
        cache_key: str,
        preferences: Optional[UserPreferences]
    ) -> List[StrategyMatch]:
        """完成匹配并缓存"""
        matches.sort(key=lambda m: (m.priority.value, m.confidence), reverse=True)
        
        if len(self._match_cache) > self._cache_size:
            oldest_key = next(iter(self._match_cache))
            del self._match_cache[oldest_key]
        
        self._match_cache[cache_key] = matches.copy()
        return matches
    
    def get_best_strategy(self, text: str, context: Optional[Dict] = None) -> Optional[StrategyMatch]:
        """获取最佳策略"""
        matches = self.match_strategies(text, context)
        return matches[0] if matches else None


class StrategyChain:
    """策略链"""
    
    def __init__(self):
        self._strategies: List[Tuple[StrategyType, StrategyConfig]] = []
        self._dependencies: Dict[StrategyType, List[StrategyType]] = defaultdict(list)
    
    def add_strategy(self, strategy_type: StrategyType, config: StrategyConfig):
        """添加策略"""
        self._strategies.append((strategy_type, config))
    
    def add_dependency(self, strategy: StrategyType, depends_on: StrategyType):
        """添加依赖关系"""
        self._dependencies[strategy].append(depends_on)
    
    def build_chain(self, matches: List[StrategyMatch]) -> List[StrategyType]:
        """构建执行链"""
        if not matches:
            return []
        
        chain = []
        processed = set()
        
        for match in sorted(matches, key=lambda m: m.priority.value, reverse=True):
            if match.strategy_type in processed:
                continue
            
            deps = self._dependencies.get(match.strategy_type, [])
            for dep in deps:
                if dep not in processed:
                    chain.append(dep)
                    processed.add(dep)
            
            chain.append(match.strategy_type)
            processed.add(match.strategy_type)
        
        return chain
    
    def execute_chain(
        self, 
        text: str, 
        chain: List[StrategyType],
        processor: Callable
    ) -> str:
        """执行策略链"""
        result = text
        for strategy_type in chain:
            try:
                result = processor(result, strategy_type)
            except Exception as e:
                logger.error(f"Strategy {strategy_type} failed: {e}")
        return result


class StrategyEngine:
    """策略引擎主类"""
    
    def __init__(self):
        self.pattern_matcher = PatternMatcher()
        self.matcher = StrategyMatcher(self.pattern_matcher)
        self.chain_builder = StrategyChain()
        self._default_preferences = UserPreferences()
        self._preferences: Optional[UserPreferences] = None
    
    def set_preferences(self, preferences: UserPreferences):
        """设置用户偏好"""
        self._preferences = preferences
    
    def get_preferences(self) -> UserPreferences:
        """获取用户偏好"""
        return self._preferences or self._default_preferences
    
    def match(
        self, 
        text: str, 
        context: Optional[Dict] = None
    ) -> List[StrategyMatch]:
        """匹配策略"""
        preferences = self.get_preferences()
        return self.matcher.match_strategies(text, context, preferences)
    
    def select_strategy(
        self, 
        text: str, 
        context: Optional[Dict] = None
    ) -> Optional[StrategyMatch]:
        """选择最佳策略"""
        return self.matcher.get_best_strategy(text, context)
    
    def build_execution_chain(
        self, 
        text: str, 
        context: Optional[Dict] = None
    ) -> List[StrategyType]:
        """构建执行链"""
        matches = self.match(text, context)
        return self.chain_builder.build_chain(matches)
    
    def process(
        self, 
        text: str, 
        processor: Callable[[str, StrategyType], str],
        context: Optional[Dict] = None
    ) -> Tuple[str, List[StrategyMatch]]:
        """处理文本"""
        matches = self.match(text, context)
        chain = self.chain_builder.build_chain(matches)
        result = self.chain_builder.execute_chain(text, chain, processor)
        return result, matches
    
    def learn_from_feedback(
        self, 
        text: str, 
        strategy: StrategyType, 
        accepted: bool
    ):
        """从反馈中学习"""
        if self._preferences:
            key = f"{text[:50]}_{strategy.value}"
            current = self._preferences.learned_preferences.get(key, 0.5)
            if accepted:
                self._preferences.learned_preferences[key] = min(1.0, current + 0.1)
            else:
                self._preferences.learned_preferences[key] = max(0.0, current - 0.1)


async def main():
    """测试策略引擎"""
    engine = StrategyEngine()
    
    test_cases = [
        ("teh quick brown fox", {"app": "textedit"}),
        ("AI 正在快速发展", {"app": "email"}),
        ("Hello, comment ça va?", {"app": "chat"}),
        ("I goes to school", {"app": "document"}),
        ("项目使用了 React 和 Node.js", {"app": "document"}),
    ]
    
    for text, context in test_cases:
        print(f"\nInput: {text}")
        strategies = engine.match(text, context)
        for s in strategies:
            print(f"  - {s.strategy_type.value}: {s.confidence:.2f} ({s.matched_patterns})")
    
    print("\nLearning from feedback...")
    engine.learn_from_feedback("teh quick brown fox", StrategyType.CORRECTION, True)
    
    print("\nTesting adaptation...")
    strategies = engine.match("teh quick brown fox", {})
    for s in strategies:
        print(f"  - {s.strategy_type.value}: {s.confidence:.2f}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
