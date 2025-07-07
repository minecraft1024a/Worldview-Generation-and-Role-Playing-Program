"""
兼容性适配器
为了保持向后兼容性，提供旧接口到新服务的适配
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any

from .services import get_service_container
from .models import CharacterModel, EnhancedGameSession, EnhancedMessage

logger = logging.getLogger(__name__)

class CompatibilityAdapter:
    """兼容性适配器类"""
    
    def __init__(self):
        self._service_container = None
        self._initialized = False
    
    async def _ensure_initialized(self):
        """确保服务已初始化"""
        if not self._initialized:
            self._service_container = await get_service_container()
            self._initialized = True
    
    def get_daily_quote(self) -> str:
        """获取每日格言（同步版本）"""
        try:
            import json
            import random
            import os
            
            quotes_path = os.path.join(os.path.dirname(__file__), 'daily_quotes.json')
            with open(quotes_path, "r", encoding="utf-8") as file:
                quotes = json.load(file).get("quotes", [])
            return random.choice(quotes) if quotes else "今日无名言，明日再试！"
        except Exception:
            return "欢迎来到WGARP世界！"
    
    def generate_world(self, background: str) -> Optional[str]:
        """生成世界观（同步版本）"""
        try:
            # 在事件循环中运行异步方法
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._generate_world_async(background))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"生成世界观失败: {e}")
            return None
    
    async def _generate_world_async(self, background: str) -> Optional[str]:
        """异步生成世界观"""
        await self._ensure_initialized()
        world_service = self._service_container.get_world_generation_service()
        
        world_desc = await world_service.generate_world(background)
        return world_desc.content if world_desc else None
    
    def generate_character(self, world_description: str, prompt: str) -> Optional[str]:
        """生成角色（同步版本）"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    self._generate_character_async(world_description, prompt)
                )
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"生成角色失败: {e}")
            return None
    
    async def _generate_character_async(self, world_description: str, prompt: str) -> Optional[str]:
        """异步生成角色"""
        await self._ensure_initialized()
        character_service = self._service_container.get_character_generation_service()
        
        character = await character_service.generate_character(world_description, prompt)
        return character.description if character else None
    
    def role_play_response(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Optional[str]:
        """角色扮演回复（同步版本）"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    self._role_play_response_async(messages, temperature)
                )
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"角色扮演回复失败: {e}")
            return None
    
    async def _role_play_response_async(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7
    ) -> Optional[str]:
        """异步角色扮演回复"""
        await self._ensure_initialized()
        
        # 这里需要更多上下文信息，暂时返回默认响应
        # 在实际使用中，应该从消息历史中提取世界观和角色信息
        return "这是一个兼容性响应，请使用新的API获得更好的体验。"

# 创建全局适配器实例
_compatibility_adapter = None

def get_compatibility_adapter() -> CompatibilityAdapter:
    """获取兼容性适配器实例"""
    global _compatibility_adapter
    if _compatibility_adapter is None:
        _compatibility_adapter = CompatibilityAdapter()
    return _compatibility_adapter

# 为了保持与旧代码的兼容性，创建模拟的旧接口
class LegacyLLMCore:
    """模拟旧的LLM核心类"""
    
    def __init__(self):
        self.adapter = get_compatibility_adapter()
    
    def generate_world(self, background: str) -> Optional[str]:
        return self.adapter.generate_world(background)
    
    def generate_character(self, world_description: str, prompt: str) -> Optional[str]:
        return self.adapter.generate_character(world_description, prompt)
    
    def role_play_response(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Optional[str]:
        return self.adapter.role_play_response(messages, temperature)

class LegacySaveManager:
    """模拟旧的存档管理器"""
    
    def __init__(self):
        self.adapter = get_compatibility_adapter()
    
    def save_game_state(self, messages, world_description, save_name=None, role=None):
        # 这里需要实现保存逻辑
        # 暂时返回一个默认的存档名
        import time
        return f"save_{int(time.time())}"
    
    def load_game_state(self, save_name: str):
        # 这里需要实现加载逻辑
        # 暂时返回空结果
        return None
    
    def get_save_list(self):
        # 这里需要实现获取存档列表的逻辑
        return []
    
    def delete_save(self, save_name: str):
        # 这里需要实现删除存档的逻辑
        return True

# 创建模拟的全局实例，保持与旧代码的兼容性
llm_core = LegacyLLMCore()
save_manager = LegacySaveManager()
