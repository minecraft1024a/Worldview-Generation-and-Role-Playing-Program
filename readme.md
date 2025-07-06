# 世界观生成与角色扮演程序

注意:这个程序由cline和copliot联合制作，因此可能会出现以下症状
- 神秘屎山代码
- 某些奇奇怪怪的bug
- 神秘环境

## 项目概述

本项目基于多种大型语言模型API构建，提供智能世界观生成与沉浸式角色扮演体验。用户可自定义世界观设定，支持智能游戏进度保存/读取，并具备完善的错误处理机制和多供应商API支持。

## 核心功能

### 世界观构建
- 自动生成包含地理、历史、文化、魔法体系等要素的原创世界观
- 支持自定义背景描述输入

### 角色扮演
- 在生成的世界中扮演自选角色
- 支持多轮对话互动与剧情分支
- 集成智能音乐播放，根据情景切换背景音乐

### 进度管理
- **智能存档**: 自动生成高质量故事摘要并优化保存游戏状态到`data`目录
- **增量更新**: 采用智能算法，高效更新摘要，减少API调用和Token消耗
- **优化命名**: 自动生成简洁有意义的存档文件名
- 支持随时读取存档继续游戏

### 多供应商支持
- 支持配置和使用来自不同大型语言模型提供商的API（如Gemini, OpenAI, Claude, DeepSeek等）
- 灵活的模型配置，可为不同任务指定不同模型

### 错误处理
- 智能识别并处理各类API错误和程序异常
- 提供中文错误提示与解决方案建议
- 支持多供应商错误处理

## 文件结构

```
Worldview-Generation-and-Role-Playing-Program/
├── main.py                  # 程序入口，包含交互式菜单
├── data/                    # 存档文件目录
│   └── *.json              # 游戏进度存档文件
├── src/                     # 核心模块
│   ├── world_generation.py  # 世界观生成引擎
│   ├── role_play.py         # 角色扮演交互系统
│   ├── error_handler.py     # 异常处理框架
│   ├── config_manager.py    # 配置管理器，处理config.toml和环境变量
│   └── summary.py          # 智能摘要生成与存档管理模块
├── config.toml              # 项目配置，包括模型、游戏设置等
├── requirements.txt         # 依赖库清单
└── .env.example             # 环境变量配置示例，包含API密钥和URL
```

## 快速启动指南

### 环境准备

首先在项目根目录下打开cmd或任意一个终端

```bash
# 安装Python 3.10+ 环境
# 安装依赖库
pip install -r requirements.txt
```

### API配置

1. 复制 `.env.example` 文件到项目根目录，并重命名为 `.env`。
2. 编辑 `.env` 文件，填入你所使用的模型提供商的API密钥和API地址。

```dotenv
# 通用API密钥 (作为回退选项)
# API_KEY=your_default_api_key_here

# 各供应商专用API密钥 (优先使用)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 各供应商API地址 (根据实际情况配置)
GEMINI_API_URL=https://generativelanguage.googleapis.com/v1beta
OPENAI_API_URL=https://api.openai.com/v1
CLAUDE_API_URL=https://api.anthropic.com
DEEPSEEK_API_URL=https://api.deepseek.com
```

请根据你在 `config.toml` 中配置的模型提供商，填写相应的 `_{PROVIDER}_API_KEY` 和 `_{PROVIDER}_API_URL`。如果未配置专用密钥，系统将尝试使用 `API_KEY` 作为通用密钥。

### 启动方式

```bash
python main.py
```

## 使用说明

### 主菜单

```
1. 读取存档继续游戏
2. 创建新世界观
3. 退出程序
```

### 游戏内指令

- `退出`：结束当前游戏
- `清屏`：清理屏幕显示
- `重新开始`：重置当前游戏
- `重新生成本回合`：重新生成最近的剧情回复
- `查看摘要`：显示当前故事的智能摘要

## 常见问题处理

| 问题类型           | 解决方案                                     |
|--------------------|----------------------------------------------|
| API访问失败        | 检查 `.env` 文件中的API_KEY和API_URL是否正确，以及网络连接是否正常。确认使用的提供商密钥已填写。 |
| 内容生成中断      | 简化世界观描述或用户输入，避免Token超限；检查模型配置的 `max_tokens`。 |
| 程序异常          | 查看控制台错误信息，参考 `error_handler.py` 处理逻辑。 |
| 摘要生成缓慢/失败 | 检查对应摘要模型的API配置和网络；调整 `config.toml` 中的摘要相关参数。 |

## 开发者指南

### 模块扩展建议

- **世界模板**：修改 `src/world_generation.py` 的prompt模板
- **角色系统**：优化 `src/role_play.py` 的交互逻辑，增加更多指令或事件处理
- **存档机制**：增强 `src/summary.py` 的智能摘要算法，优化关键词提取或摘要结构
- **音乐系统**: 扩展 `src/music_player.py` 支持更多音乐源或控制方式
- **UI优化**: 使用更丰富的Rich库功能美化控制台输出

### 配置说明

- `config.toml`: 包含游戏设置（如摘要间隔 `game.summary_interval`）和各模型（`world_generation`, `role_play`, `music_mood`, `save_summary`, `smart_summary`, `save_name`, `character_generation`）的提供商、模型名称、温度、最大Token等参数。
- `.env`: 存储敏感信息，如API密钥和API地址。请勿将此文件提交到版本控制。

## 许可证

GPL3 License © 2025 Developer
