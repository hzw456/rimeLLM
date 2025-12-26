# Change: AI Clipboard - 智能输入增强工具

## Why

当前的文本输入工具缺乏智能化能力，用户在进行文本纠错、扩写、翻译等操作时需要手动切换不同的工具，效率低下且体验不佳。通过集成 Rime 输入法框架和 AI 大模型能力，可以实现场景感知、无缝集成和智能自动化的文本输入体验。

## What Changes

- 新增 Rime 输入法集成层，实现输入上下文捕获和建议注入
- 新增 AI Provider 抽象层，支持 OpenAI、Claude、本地模型等多模型对接
- 新增核心文本处理功能（纠错、扩写、翻译、摘要）
- 新增策略引擎，根据场景自动匹配优化策略
- 新增用户配置界面，支持 API Key 管理、模型选择、规则定制

## Impact

- Affected specs: rime-integration, ai-abstraction, text-processing, strategy-engine, user-configuration
- Affected code: 核心框架模块、AI Provider 模块、Rime 集成模块、用户配置界面
