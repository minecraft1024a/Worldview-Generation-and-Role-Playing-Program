# 世界观生成与角色扮演程序

## 功能简介
本程序包含两个核心模块：
1. **src/world_generation.py** - 调用OpenAI API生成完整世界观设定
2. **src/role_play.py** - 基于生成的世界观进行角色扮演游戏交互

主程序main.py提供交互式菜单，用户可选择：
- 生成新世界观
- 进入角色扮演模式
- 退出程序

## 安装说明
1. 安装Python 3.10+环境
2. 安装依赖库：
```bash
pip install -r requirements.txt
```
3. 创建.env文件并填写API信息：
```env
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=your_api_base
OPENAI_MODEL_NAME=your_MODEL_NAME
```

## 使用说明
1. 运行程序：
```bash
python main.py
```
2. 在主菜单选择操作：
   - 输入`1`生成世界观
   - 输入`2`进入角色扮演模式
   - 输入`3`退出程序

## 依赖库
- openai>=1.0.0
- python-dotenv>=1.0.0

## 注意事项
1. 需要有效API密钥
2. 网络连接需保持畅通
3. 生成内容长度受模型token限制影响
