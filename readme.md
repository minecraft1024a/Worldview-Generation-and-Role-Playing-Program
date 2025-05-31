# 世界观生成与角色扮演程序

## 项目简介
本程序提供基于AI的动态世界观构建与沉浸式角色扮演体验。通过OpenAI API实现：
1. **智能世界观生成** - 自动创建包含地理/历史/文化等要素的完整世界观
2. **角色交互系统** - 在生成的世界中进行多轮角色扮演对话

## 功能模块
### 世界生成模块 (src/world_generation.py)
- 调用大语言模型生成多维度世界观设定
- 支持自定义生成参数（如文明类型、魔法体系等）

### 角色扮演模块 (src/role_play.py)
- 基于生成的世界观进行角色扮演交互
- 支持多角色切换与动态对话系统

### 主程序 (main.py)
提供交互式菜单：
```bash
1. 生成新世界观
2. 进入角色扮演模式
3. 退出程序
```

## 安装指南
1. 环境要求
   - Python 3.10+（建议使用virtualenv）
   - OpenAI官方库（v1.0.0+）
   - python-dotenv库

2. 安装步骤
```bash
# 安装依赖
pip install -r requirements.txt

# 配置API凭证
echo "API_KEY=your_api_key
API_BASE=https://api.openai.com/v1
MODEL_NAME=gpt-4o" > .env
```

## 快速启动
```bash
# 运行程序
python main.py

# 交互流程示例
1. 选择[1]生成世界观
2. 输入世界特征描述（如"蒸汽朋克+赛博江湖"）
3. 选择[3]进入角色扮演模式
4. 输入角色特征（如"少林武僧+机械义肢"）
5. 开始沉浸式对话
```

## 系统依赖
- openai>=1.0.0
- python-dotenv>=1.0.0

## 注意事项
⚠️ **API访问**：需要有效OpenAI API密钥及网络连接  
📝 **内容限制**：生成内容长度受模型token限制（默认4096 tokens）  
🔄 **错误处理**：网络异常时会自动重试（src/error_handler.py）

## 开发贡献
欢迎提交PR改进：
1. 添加更多世界观生成模板
2. 优化角色扮演对话逻辑
3. 扩展错误处理机制

MIT License © 2025 Deleople
