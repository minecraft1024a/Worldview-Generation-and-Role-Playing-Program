"""
WGARP 统一启动脚本
提供多种启动模式：终端版、Web版、服务模式
"""

import sys
import os
import argparse
import asyncio
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_logging(level: str = "INFO"):
    """设置日志"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('wgarp.log', encoding='utf-8')
        ]
    )

async def start_terminal_mode():
    """启动终端模式"""
    print("正在启动WGARP终端版...")
    
    try:
        # 导入终端版主程序
        from main import main as terminal_main
        await terminal_main()
    except ImportError:
        print("错误: 无法导入终端版主程序")
        return False
    except Exception as e:
        print(f"终端版启动失败: {e}")
        return False
    
    return True

async def start_web_mode(host: str = "127.0.0.1", port: int = 8000):
    """启动Web模式"""
    print(f"正在启动WGARP Web版... (http://{host}:{port})")
    
    try:
        import uvicorn
        from backend.main import app
        
        # 启动FastAPI服务器
        config = uvicorn.Config(
            app=app,
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
        
    except ImportError:
        print("错误: 缺少Web服务依赖，请安装backend/requirements.txt中的依赖")
        return False
    except Exception as e:
        print(f"Web版启动失败: {e}")
        return False
    
    return True

async def start_service_mode():
    """启动服务模式（仅后端API）"""
    print("正在启动WGARP服务模式...")
    
    try:
        from src.services import initialize_services
        
        # 初始化所有服务
        service_container = await initialize_services()
        print("所有服务已启动，等待调用...")
        
        # 保持服务运行
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n正在关闭服务...")
            await service_container.shutdown()
            print("服务已关闭")
            
    except Exception as e:
        print(f"服务模式启动失败: {e}")
        return False
    
    return True

def check_dependencies():
    """检查依赖"""
    missing_deps = []
    
    # 检查基本依赖
    try:
        import toml
    except ImportError:
        missing_deps.append("toml")
    
    try:
        import requests
    except ImportError:
        missing_deps.append("requests")
    
    # 检查可选依赖
    optional_deps = []
    
    try:
        import pygame
    except ImportError:
        optional_deps.append("pygame (音乐功能)")
    
    try:
        import rich
    except ImportError:
        optional_deps.append("rich (终端美化)")
    
    if missing_deps:
        print("错误: 缺少必要依赖:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\n请运行: pip install -r requirements.txt")
        return False
    
    if optional_deps:
        print("警告: 缺少可选依赖，某些功能可能不可用:")
        for dep in optional_deps:
            print(f"  - {dep}")
        print()
    
    return True

def check_config():
    """检查配置文件"""
    config_path = project_root / "config.toml"
    if not config_path.exists():
        print("警告: 未找到config.toml配置文件")
        print("请复制config.toml.example并修改配置")
        return False
    return True

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="WGARP - 世界观生成与角色扮演程序")
    parser.add_argument(
        "mode", 
        choices=["terminal", "web", "service"],
        nargs="?",
        default="terminal",
        help="启动模式: terminal(终端版), web(Web版), service(服务模式)"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Web模式的主机地址")
    parser.add_argument("--port", type=int, default=8000, help="Web模式的端口号")
    parser.add_argument("--log-level", default="INFO", help="日志级别")
    parser.add_argument("--check", action="store_true", help="仅检查环境和配置")
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.log_level)
    
    print("=" * 60)
    print("    WGARP - 世界观生成与角色扮演程序")
    print("    Worldview Generation and Role-Playing Program")
    print("=" * 60)
    print()
    
    # 检查环境
    print("正在检查环境...")
    if not check_dependencies():
        return 1
    
    if not check_config():
        return 1
    
    print("环境检查完成✓")
    print()
    
    if args.check:
        print("环境检查完成，所有依赖和配置正常")
        return 0
    
    # 根据模式启动
    success = False
    try:
        if args.mode == "terminal":
            success = await start_terminal_mode()
        elif args.mode == "web":
            success = await start_web_mode(args.host, args.port)
        elif args.mode == "service":
            success = await start_service_mode()
    except KeyboardInterrupt:
        print("\n用户中断，正在退出...")
    except Exception as e:
        print(f"启动过程中发生错误: {e}")
        logging.exception("启动失败")
    
    return 0 if success else 1

if __name__ == "__main__":
    if sys.platform == "win32":
        # Windows下设置事件循环策略
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
