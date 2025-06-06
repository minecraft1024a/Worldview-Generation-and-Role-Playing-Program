# 世界观生成与角色扮演程序
注意:这个程序由cline和copliot联合制作，因此可能会出现以下症状
- 神秘屎山代码
- 某些奇奇怪怪的bug
- 神秘环境

## 项目概述
本项目基于OpenAI API构建，提供智能世界观生成与沉浸式角色扮演体验。用户可自定义世界观设定，支持游戏进度保存/读取，并具备完善的错误处理机制。

## 核心功能
### 世界观构建
- 自动生成包含地理、历史、文化、魔法体系等要素的原创世界观
- 支持自定义背景描述输入

### 角色扮演
- 在生成的世界中扮演自选角色
- 支持多轮对话互动与剧情分支

### 进度管理
- 自动保存游戏状态到`data`
- 支持随时读取存档继续游戏

### 错误处理
- 智能识别OpenAI API各类错误类型
- 提供中文错误提示与解决方案建议

## 文件结构
```
Worldview-Generation-and-Role-Playing-Program/
├── main.py                  # 程序入口，包含交互式菜单
├── data/                    # 存档文件目录
│   └── summary.json        # 游戏进度存档模板
├── src/                     # 核心模块
│   ├── world_generation.py  # 世界观生成引擎
│   ├── role_play.py         # 角色扮演交互系统
│   ├── error_handler.py     # 异常处理框架
│   ├── load_summary.py      # 存档加载模块
│   └── summary.py          # 对话摘要生成器
├── requirements.txt         # 依赖库清单
└── .env                     # API配置文件
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
在`.env`文件中配置：
```
API_KEY=your_openai_api_key
API_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o
```

## 使用说明
### 启动方式
```bash
python main.py
```

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

## 常见问题处理
| 问题类型           | 解决方案                          |
|--------------------|-----------------------------------|
| API访问失败        | 检查API_KEY有效性与网络连接       |
| 内容生成中断      | 简化世界观描述，避免token超限     |
| 程序异常          | 查看控制台错误代码，参考error_handler处理逻辑 |

## 开发者指南
### 模块扩展建议
- **世界模板**：修改`src/world_generation.py`的prompt模板
- **角色系统**：优化`src/role_play.py`的交互逻辑
- **存档机制**：增强`src/summary.py`的摘要生成算法

## 许可证
MIT License © 2025 Deleople
