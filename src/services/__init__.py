"""
服务层初始化
集中管理所有服务的实例化和依赖注入
"""

import logging
from typing import Optional

from ..core.config import ConfigManager
from ..core.llm import LLMService
from ..utils.error_handler import ErrorHandler

from .world_generation import WorldGenerationService
from .character_generation import CharacterGenerationService
from .role_play import RolePlayService
from .save_manager import SaveManager
from .save_loader import SaveLoaderService
from .music_service import MusicService

logger = logging.getLogger(__name__)

class ServiceContainer:
    """服务容器，负责管理所有服务的生命周期"""
    
    def __init__(self):
        # 核心服务
        self.config_manager: Optional[ConfigManager] = None
        self.llm_service: Optional[LLMService] = None
        self.error_handler: Optional[ErrorHandler] = None
        
        # 业务服务
        self.world_generation_service: Optional[WorldGenerationService] = None
        self.character_generation_service: Optional[CharacterGenerationService] = None
        self.role_play_service: Optional[RolePlayService] = None
        self.save_manager: Optional[SaveManager] = None
        self.save_loader_service: Optional[SaveLoaderService] = None
        self.music_service: Optional[MusicService] = None
        
        self._initialized = False
    
    async def initialize(self, config_path: str = "config.toml"):
        """
        初始化所有服务
        
        Args:
            config_path: 配置文件路径
        """
        try:
            logger.info("开始初始化服务容器...")
            
            # 1. 初始化核心服务
            self.config_manager = ConfigManager(config_path)
            self.error_handler = ErrorHandler()
            self.llm_service = LLMService(self.config_manager, self.error_handler)
            
            # 2. 初始化业务服务
            self.world_generation_service = WorldGenerationService(
                self.llm_service, 
                self.error_handler
            )
            
            self.character_generation_service = CharacterGenerationService(
                self.llm_service,
                self.error_handler
            )
            
            self.role_play_service = RolePlayService(
                self.llm_service,
                self.error_handler
            )
            
            self.save_manager = SaveManager(
                self.llm_service,
                self.error_handler
            )
            
            self.save_loader_service = SaveLoaderService(
                self.save_manager,
                self.error_handler
            )
            
            self.music_service = MusicService(
                self.error_handler
            )
            
            # 3. 应用配置
            await self._apply_configurations()
            
            self._initialized = True
            logger.info("服务容器初始化完成")
            
        except Exception as e:
            logger.error(f"服务容器初始化失败: {e}")
            raise
    
    async def _apply_configurations(self):
        """应用配置到各个服务"""
        try:
            config = self.config_manager.get_config()
            
            # 配置音乐服务
            if self.music_service:
                music_enabled = config.get('game', {}).get('enable_music', False)
                self.music_service.enable_music(music_enabled)
                
                music_volume = config.get('game', {}).get('music_volume', 0.7)
                self.music_service.set_volume(music_volume)
            
            # 配置LLM服务
            if self.llm_service:
                await self.llm_service.initialize()
            
        except Exception as e:
            logger.error(f"应用配置失败: {e}")
            # 不抛出异常，允许服务在默认配置下运行
    
    def is_initialized(self) -> bool:
        """检查服务容器是否已初始化"""
        return self._initialized
    
    def get_world_generation_service(self) -> WorldGenerationService:
        """获取世界观生成服务"""
        if not self._initialized:
            raise RuntimeError("服务容器未初始化")
        return self.world_generation_service
    
    def get_character_generation_service(self) -> CharacterGenerationService:
        """获取角色生成服务"""
        if not self._initialized:
            raise RuntimeError("服务容器未初始化")
        return self.character_generation_service
    
    def get_role_play_service(self) -> RolePlayService:
        """获取角色扮演服务"""
        if not self._initialized:
            raise RuntimeError("服务容器未初始化")
        return self.role_play_service
    
    def get_save_manager(self) -> SaveManager:
        """获取存档管理器"""
        if not self._initialized:
            raise RuntimeError("服务容器未初始化")
        return self.save_manager
    
    def get_save_loader_service(self) -> SaveLoaderService:
        """获取存档加载服务"""
        if not self._initialized:
            raise RuntimeError("服务容器未初始化")
        return self.save_loader_service
    
    def get_music_service(self) -> MusicService:
        """获取音乐服务"""
        if not self._initialized:
            raise RuntimeError("服务容器未初始化")
        return self.music_service
    
    def get_config_manager(self) -> ConfigManager:
        """获取配置管理器"""
        if not self._initialized:
            raise RuntimeError("服务容器未初始化")
        return self.config_manager
    
    def get_llm_service(self) -> LLMService:
        """获取LLM服务"""
        if not self._initialized:
            raise RuntimeError("服务容器未初始化")
        return self.llm_service
    
    def get_error_handler(self) -> ErrorHandler:
        """获取错误处理器"""
        if not self._initialized:
            raise RuntimeError("服务容器未初始化")
        return self.error_handler
    
    async def shutdown(self):
        """关闭服务容器"""
        try:
            logger.info("开始关闭服务容器...")
            
            # 停止音乐播放
            if self.music_service:
                self.music_service.stop_music()
            
            # 关闭LLM服务
            if self.llm_service:
                await self.llm_service.shutdown()
            
            self._initialized = False
            logger.info("服务容器关闭完成")
            
        except Exception as e:
            logger.error(f"关闭服务容器时发生错误: {e}")


# 全局服务容器实例
_service_container: Optional[ServiceContainer] = None

async def get_service_container() -> ServiceContainer:
    """获取全局服务容器实例"""
    global _service_container
    if _service_container is None:
        _service_container = ServiceContainer()
        await _service_container.initialize()
    return _service_container

async def initialize_services(config_path: str = "config.toml") -> ServiceContainer:
    """初始化服务容器"""
    global _service_container
    _service_container = ServiceContainer()
    await _service_container.initialize(config_path)
    return _service_container

async def shutdown_services():
    """关闭所有服务"""
    global _service_container
    if _service_container:
        await _service_container.shutdown()
        _service_container = None
