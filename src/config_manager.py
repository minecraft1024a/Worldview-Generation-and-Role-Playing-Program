import toml
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class ConfigManager:
    """配置管理器，统一管理所有配置项"""
    
    def __init__(self, config_path='config.toml'):
        self.config_path = config_path
        self.config = toml.load(config_path)
        self._validate_config()
    
    def _validate_config(self):
        """验证配置文件的完整性"""
        required_sections = ['game', 'models']
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"配置文件缺少必需的 '{section}' 部分")
    
    def get_game_config(self):
        """获取游戏相关配置"""
        return self.config['game']
    
    def get_model_config(self, model_type):
        """获取指定类型的模型配置"""
        if model_type not in self.config['models']:
            raise ValueError(f"未找到模型类型 '{model_type}' 的配置")
        
        model_config = self.config['models'][model_type]
        provider = model_config['provider']
        
        # 从环境变量获取对应提供商的 API 地址
        api_url_key = f"{provider.upper()}_API_URL"
        api_url = os.getenv(api_url_key)
        
        if not api_url:
            raise ValueError(f"未找到提供商 '{provider}' 的 API 地址配置 '{api_url_key}'")
        
        return {
            'model_name': model_config['model'],
            'provider': provider,
            'api_url': api_url,
            'temperature': model_config.get('temperature', 0.7),
            'max_tokens': model_config.get('max_tokens', None),
            'timeout': model_config.get('timeout', 30)
        }
    
    def get_all_providers(self):
        """获取所有配置的提供商"""
        providers = set()
        for model_config in self.config['models'].values():
            providers.add(model_config['provider'])
        return list(providers)
    
    def get_api_key(self, provider=None):
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
    
    def reload_config(self):
        """重新加载配置文件"""
        self.config = toml.load(self.config_path)
        self._validate_config()

# 创建全局配置管理器实例
config_manager = ConfigManager()
