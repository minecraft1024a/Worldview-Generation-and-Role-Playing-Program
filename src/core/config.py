"""
WGARP 配置管理器 - 重构版本
统一管理所有配置项，支持环境变量和配置文件，提供更好的错误处理和默认值
"""

import toml
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List
from pathlib import Path
import sys

# 加载环境变量
load_dotenv()

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class ConfigManager:
    """配置管理器，统一管理所有配置项"""
    
    def __init__(self, config_path: str = 'config.toml'):
        self.config_path = project_root / config_path
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_path):
                return toml.load(self.config_path)
            else:
                print(f"警告: 配置文件 {self.config_path} 不存在，使用默认配置")
                return self._get_default_config()
        except Exception as e:
            print(f"警告: 加载配置文件失败 {e}，使用默认配置")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'game': {
                'summary_interval': 3,
                'enable_music': False,
                'max_message_history': 100,
                'auto_save_interval': 300,  # 秒
                'data_directory': 'data'
            },
            'models': {
                'world_generation': {
                    'provider': 'gemini',
                    'model': 'gemini-2.5-flash',
                    'temperature': 0.7,
                    'max_tokens': 2000,
                    'timeout': 30
                },
                'role_play': {
                    'provider': 'gemini',
                    'model': 'gemini-2.5-flash',
                    'temperature': 0.7,
                    'max_tokens': 1500,
                    'timeout': 30
                },
                'smart_summary': {
                    'provider': 'gemini',
                    'model': 'gemini-2.5-flash',
                    'temperature': 0.4,
                    'max_tokens': 800,
                    'timeout': 25
                },
                'save_summary': {
                    'provider': 'gemini',
                    'model': 'gemini-2.5-flash',
                    'temperature': 0.3,
                    'max_tokens': 400,
                    'timeout': 20
                },
                'character_generation': {
                    'provider': 'gemini',
                    'model': 'gemini-2.5-flash',
                    'temperature': 0.6,
                    'max_tokens': 800,
                    'timeout': 25
                },
                'music_mood': {
                    'provider': 'gemini',
                    'model': 'gemini-2.5-flash',
                    'temperature': 0.3,
                    'max_tokens': 50,
                    'timeout': 15
                },
                'save_name': {
                    'provider': 'gemini',
                    'model': 'gemini-2.5-flash',
                    'temperature': 0.4,
                    'max_tokens': 50,
                    'timeout': 15
                }
            },
            'api': {
                'retry_attempts': 3,
                'retry_delay': 1.0,
                'request_timeout': 30,
                'max_concurrent_requests': 5
            },
            'web': {
                'host': '0.0.0.0',
                'port': 8000,
                'cors_origins': ['http://localhost:3000', 'http://127.0.0.1:3000'],
                'websocket_timeout': 300,
                'max_connections': 100
            }
        }
    
    def _validate_config(self):
        """验证配置"""
        required_sections = ['game', 'models']
        default_config = self._get_default_config()
        
        for section in required_sections:
            if section not in self.config:
                print(f"警告: 配置文件缺少 '{section}' 部分，使用默认配置")
                self.config[section] = default_config[section]
    
    def get_game_config(self) -> Dict[str, Any]:
        """获取游戏相关配置"""
        return self.config.get('game', self._get_default_config()['game'])
    
    def get_model_config(self, model_type: str) -> Dict[str, Any]:
        """获取指定类型的模型配置"""
        models_config = self.config.get('models', {})
        model_config = models_config.get(model_type)
        
        if not model_config:
            # 使用默认配置
            default_models = self._get_default_config()['models']
            model_config = default_models.get(model_type, default_models['role_play'])
            print(f"警告: 未找到模型 '{model_type}' 的配置，使用默认配置")
        
        provider = model_config['provider']
        
        # 从环境变量获取对应提供商的 API 地址
        api_url_key = f"{provider.upper()}_API_URL"
        api_url = os.getenv(api_url_key)
        
        if not api_url:
            print(f"警告: 未找到提供商 '{provider}' 的 API 地址配置 '{api_url_key}'")
            api_url = "https://api.openai.com/v1"  # 默认地址
        
        return {
            'model_name': model_config['model'],
            'provider': provider,
            'api_url': api_url,
            'temperature': model_config.get('temperature', 0.7),
            'max_tokens': model_config.get('max_tokens', None),
            'timeout': model_config.get('timeout', 30)
        }
    
    def get_all_providers(self) -> List[str]:
        """获取所有配置的提供商"""
        providers = set()
        models_config = self.config.get('models', {})
        for model_config in models_config.values():
            providers.add(model_config.get('provider', 'gemini'))
        return list(providers)
    
    def get_api_key(self, provider: Optional[str] = None) -> str:
        """获取指定提供商的 API 密钥"""
        if provider:
            # 根据提供商获取对应的API密钥
            api_key_var = f"{provider.upper()}_API_KEY"
            api_key = os.getenv(api_key_var)
            if api_key:
                return api_key
        
        # 回退到通用的API_KEY
        api_key = os.getenv("API_KEY")
        if not api_key:
            provider_msg = f"提供商 '{provider}' 的专用密钥 '{provider.upper()}_API_KEY' 或" if provider else ""
            raise ValueError(f"未找到 {provider_msg}通用的 'API_KEY' 环境变量")
        return api_key
    
    def get_api_config(self) -> Dict[str, Any]:
        """获取 API 相关配置"""
        return self.config.get('api', self._get_default_config()['api'])
    
    def get_web_config(self) -> Dict[str, Any]:
        """获取 Web 相关配置"""
        return self.config.get('web', self._get_default_config()['web'])
    
    def get_data_directory(self) -> str:
        """获取数据目录路径"""
        return self.get_game_config().get('data_directory', 'data')
    
    def get_music_enabled(self) -> bool:
        """获取音乐是否启用"""
        return self.get_game_config().get('enable_music', False)
    
    def get_summary_interval(self) -> int:
        """获取摘要生成间隔"""
        return self.get_game_config().get('summary_interval', 3)
    
    def reload_config(self):
        """重新加载配置文件"""
        self.config = self._load_config()
        self._validate_config()
    
    def save_config(self, config_data: Dict[str, Any] = None):
        """保存配置到文件"""
        try:
            config_to_save = config_data or self.config
            with open(self.config_path, 'w', encoding='utf-8') as f:
                toml.dump(config_to_save, f)
            print(f"配置已保存到 {self.config_path}")
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def update_model_config(self, model_type: str, **kwargs):
        """更新模型配置"""
        if 'models' not in self.config:
            self.config['models'] = {}
        if model_type not in self.config['models']:
            self.config['models'][model_type] = {}
        
        self.config['models'][model_type].update(kwargs)
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"ConfigManager(config_path='{self.config_path}')"
    
    def __repr__(self) -> str:
        """对象表示"""
        return self.__str__()


# 创建全局配置管理器实例
config_manager = ConfigManager()
