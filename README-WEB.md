# WGARP Web 版本 - 部署与使用指南

## 概述

WGARP (世界观生成与角色扮演程序) Web 版本是原命令行程序的现代化重构版本，采用 FastAPI + React 技术栈，提供了美观的 Web 界面和更好的用户体验。

## 技术栈

- **后端**: FastAPI + Python 3.8+
- **前端**: React 18 + Material-UI
- **通信**: REST API + WebSocket
- **AI服务**: 支持多种 LLM 提供商 (OpenAI, Gemini, Claude, DeepSeek)

## 快速开始

### 方法一：一键启动（推荐）

1. 确保已安装以下依赖：
   - Python 3.8+
   - Node.js 16+
   - npm

2. 配置环境变量：
   ```bash
   # 复制环境变量模板
   copy .env.example .env
   
   # 编辑 .env 文件，填入您的 API 密钥
   ```

3. 运行一键启动脚本：
   ```bash
   start-web.bat
   ```

4. 等待服务启动完成后，打开浏览器访问：
   - 前端应用: http://localhost:3000
   - 后端 API: http://localhost:8000
   - API 文档: http://localhost:8000/docs

### 方法二：分别启动

#### 启动后端

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务器
python main.py
```

#### 启动前端

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm start
```

## 功能特性

### 🌍 智能世界观生成
- 基于用户描述生成详细的世界观设定
- 支持多种主题：魔法、科幻、古代、现代等
- 可重新生成和修改

### 🎭 沉浸式角色扮演
- 实时 WebSocket 通信，流畅的对话体验
- 智能 AI 响应，丰富的剧情发展
- 支持自由文本输入和指令

### 💾 智能存档系统
- 自动生成游戏摘要
- 智能存档命名
- 支持多存档管理
- 存档预览和删除功能

### 🎨 现代化界面
- 响应式设计，支持桌面和移动设备
- Material Design 风格，美观直观
- 实时消息展示，支持 Markdown 渲染
- 深色/浅色主题支持

## 目录结构

```
WGARP/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   └── __init__.py
│   ├── main.py             # 应用入口
│   └── requirements.txt    # Python 依赖
├── frontend/               # React 前端
│   ├── public/            # 静态资源
│   ├── src/
│   │   ├── components/    # React 组件
│   │   ├── pages/         # 页面组件
│   │   ├── services/      # API 服务
│   │   ├── hooks/         # 自定义 Hook
│   │   └── App.js         # 主应用组件
│   └── package.json       # Node.js 依赖
├── src/                   # 原始业务逻辑模块
├── data/                  # 存档数据目录
├── config.toml            # 配置文件
├── .env.example           # 环境变量模板
└── start-web.bat          # 一键启动脚本
```

## API 接口

### REST API

- `GET /api/v1/daily-quote` - 获取每日格言
- `POST /api/v1/generate-world` - 生成世界观
- `POST /api/v1/generate-character` - 生成角色
- `POST /api/v1/role-play` - 角色扮演回复
- `POST /api/v1/save-game` - 保存游戏
- `GET /api/v1/load-game/{save_name}` - 加载游戏
- `GET /api/v1/saves` - 获取存档列表
- `DELETE /api/v1/saves/{save_name}` - 删除存档

### WebSocket

- `/ws` - 实时游戏通信
  - `start_game` - 开始新游戏
  - `load_game` - 加载游戏
  - `player_action` - 玩家行动
  - `save_game` - 保存游戏

## 配置说明

### 环境变量配置

编辑 `.env` 文件：

```env
# API 密钥
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
CLAUDE_API_KEY=your_claude_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key

# API 地址
GEMINI_API_URL=https://generativelanguage.googleapis.com/v1beta
OPENAI_API_URL=https://api.openai.com/v1
CLAUDE_API_URL=https://api.anthropic.com
DEEPSEEK_API_URL=https://api.deepseek.com
```

### 模型配置

编辑 `config.toml` 文件来配置不同功能使用的模型：

```toml
[models.world_generation]
provider = "gemini"
model = "gemini-2.5-flash"
temperature = 0.7
max_tokens = 2000

[models.role_play]
provider = "gemini"
model = "gemini-2.5-flash"
temperature = 0.7
max_tokens = 1500
```

## 部署到生产环境

### 后端部署

1. 使用 Gunicorn 作为 WSGI 服务器：
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. 使用 Docker 部署：
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### 前端部署

1. 构建生产版本：
```bash
npm run build
```

2. 使用 Nginx 提供静态文件服务：
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        root /path/to/build;
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 故障排除

### 常见问题

1. **后端启动失败**
   - 检查 Python 版本是否为 3.8+
   - 确认已安装所有依赖：`pip install -r requirements.txt`
   - 检查端口 8000 是否被占用

2. **前端启动失败**
   - 检查 Node.js 版本是否为 16+
   - 清除缓存：`npm ci`
   - 检查端口 3000 是否被占用

3. **API 调用失败**
   - 检查 `.env` 文件中的 API 密钥是否正确
   - 确认网络连接正常
   - 查看后端日志获取详细错误信息

4. **WebSocket 连接失败**
   - 确认后端服务正常运行
   - 检查防火墙设置
   - 确认浏览器支持 WebSocket

### 日志查看

- 后端日志：在终端中直接查看输出
- 前端日志：打开浏览器开发者工具的 Console 标签
- API 文档：访问 http://localhost:8000/docs

## 开发指南

### 添加新功能

1. **后端**：
   - 在 `app/api/routes.py` 中添加新的 API 端点
   - 在 `app/services/wgarp_service.py` 中添加业务逻辑
   - 在 `app/models/__init__.py` 中定义数据模型

2. **前端**：
   - 在 `src/services/api.js` 中添加 API 调用函数
   - 在 `src/pages/` 中创建新页面组件
   - 在 `src/App.js` 中添加路由

### 调试技巧

- 使用 `console.log()` 进行前端调试
- 使用 Python `print()` 进行后端调试
- 利用浏览器开发者工具查看网络请求
- 查看 FastAPI 自动生成的 API 文档

## 贡献指南

1. Fork 本项目
2. 创建功能分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送分支：`git push origin feature/new-feature`
5. 创建 Pull Request

## 许可证

本项目基于 GPL-3.0 许可证开源。详见 LICENSE 文件。

## 联系方式

- 作者：xxx
- QQ 群：123456
- 项目地址：https://github.com/your-username/wgarp

## 更新日志

### v2.1.0-web (当前版本)
- ✨ 全新 Web 界面，基于 React + Material-UI
- 🔄 FastAPI 后端重构，提供 REST API 和 WebSocket 支持
- 💾 改进的存档系统，支持可视化管理
- 🎨 响应式设计，支持多设备访问
- 🔧 更好的错误处理和用户反馈

### v2.0.0 (命令行版本)
- 智能摘要系统
- 多 LLM 支持
- 音乐播放功能
- Rich 美化界面
