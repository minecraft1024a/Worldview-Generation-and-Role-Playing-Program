# 世界观生成与角色扮演程序

## 项目简介
本项目基于 OpenAI API，提供智能世界观生成与沉浸式角色扮演体验。用户可自定义世界观设定，保存和读取游戏进度，并在丰富的虚拟世界中进行多轮角色扮演互动。

## 主要功能

- **世界观生成**：自动生成包含地理、历史、文化、魔法体系等要素的原创世界观，支持自定义背景描述。
- **角色扮演系统**：在生成的世界中扮演自选角色，与 AI 进行多轮互动，体验动态剧情。
- **存档管理**：支持将游戏进度保存为 summary.json，并可随时读取存档继续冒险。
- **错误处理**：内置完善的异常处理机制，保障程序稳定运行。

## 目录结构

```
Worldview-Generation-and-Role-Playing-Program/
├── main.py                  # 主程序入口，交互式菜单
├── data/
│   └── summary.json         # 游戏存档文件
├── src/
│   ├── world_generation.py  # 世界观生成模块
│   ├── role_play.py         # 角色扮演模块
│   ├── error_handler.py     # 错误处理模块
│   └── load_summary.py      # 存档读取模块
├── requirements.txt         # 依赖列表
└── readme.md                # 项目说明
```

## 安装与配置

1. **环境要求**
   - Python 3.10 及以上
   - OpenAI 官方库 >= 1.0.0
   - python-dotenv

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **API 配置**
   已有 `.env` 文件，请确保内容包含如下字段，并已正确填写你的 OpenAI API 信息：
   ```
   API_KEY=你的OpenAI_API密钥
   API_URL=https://api.openai.com/v1
   MODEL_NAME=gpt-4o
   ```

## 使用方法

1. **启动程序**
   ```bash
   python main.py
   ```

2. **主菜单选项**
   ```
   1. 读取存档开始游戏
   2. 开始新游戏
   3. 退出
   ```

3. **流程示例**
   - 选择 [1] 可直接读取上次存档继续冒险
   - 选择 [2] 输入世界观背景，生成新世界观并进入角色扮演
   - 游戏过程中可随时保存进度，支持多轮对话与剧情分支

## 常见问题

- **API 访问失败**：请检查 API_KEY 是否正确，网络连接是否正常。
- **内容生成受限**：受模型 token 限制，建议简明描述世界观和角色。
- **程序异常**：详细错误信息会在控制台输出，便于排查。

## 贡献与反馈

欢迎提交 PR 或 issue 参与改进：
- 丰富世界观模板
- 优化角色扮演体验
- 增强存档与恢复机制

---

MIT License © 2025 Deleople
