"""
WGARP Web服务适配层
将重构后的服务层适配到Web API
"""

import sys
import os
import json
import random
import asyncio
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.services import get_service_container, ServiceContainer
from src.models import CharacterModel, EnhancedGameSession, EnhancedMessage, WorldConfig

class WGARPService:
    """WGARP Web服务类，封装所有核心业务逻辑"""
    
    def __init__(self):
        self.service_container: Optional[ServiceContainer] = None
        self._initialized = False
    
    async def initialize(self):
        """初始化服务"""
        if not self._initialized:
            self.service_container = await get_service_container()
            self._initialized = True
    
    async def get_daily_quote(self) -> str:
        """获取每日格言"""
        try:
            quotes_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src', 'daily_quotes.json')
            with open(quotes_path, "r", encoding="utf-8") as file:
                quotes = json.load(file).get("quotes", [])
            return random.choice(quotes) if quotes else "今日无名言，明日再试！"
        except Exception:
            return "欢迎来到WGARP世界！"
    
    async def generate_world(self, background: str, config: Optional[Dict[str, Any]] = None) -> Tuple[str, bool, str]:
        """生成世界观"""
        try:
            await self.initialize()
            world_service = self.service_container.get_world_generation_service()
            
            # 创建世界观配置
            world_config = WorldConfig(
                theme=config.get("theme", "") if config else "",
                style=config.get("style", "") if config else "",
                complexity=config.get("complexity", "") if config else "",
                language=config.get("language", "中文") if config else "中文"
            )
            
            world_desc = await world_service.generate_world(background, world_config)
            if world_desc:
                return world_desc.content, True, ""
            else:
                return "", False, "世界观生成失败"
                
        except Exception as e:
            return "", False, f"生成世界观时发生错误: {str(e)}"
    
    async def generate_character(self, world_description: str, prompt: str) -> Tuple[str, bool, str]:
        """生成角色"""
        try:
            await self.initialize()
            character_service = self.service_container.get_character_generation_service()
            
            character = await character_service.generate_character(
                world_description=world_description,
                prompt=prompt
            )
            
            if character:
                return character.description, True, ""
            else:
                return "", False, "角色生成失败"
                
        except Exception as e:
            return "", False, f"生成角色时发生错误: {str(e)}"
    
    async def start_role_play_session(
        self, 
        world_description: str, 
        character_description: str,
        character_name: str = "",
        summary_text: Optional[str] = None,
        last_conversation: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[Optional[str], bool, str]:
        """开始角色扮演会话"""
        try:
            await self.initialize()
            roleplay_service = self.service_container.get_role_play_service()
            
            # 创建角色模型
            character = CharacterModel(
                name=character_name or "角色",
                description=character_description,
                world_context=world_description
            )
            
            # 转换历史消息
            messages = []
            if last_conversation:
                for msg in last_conversation:
                    messages.append(EnhancedMessage(
                        role=msg.get("role", "user"),
                        content=msg.get("content", ""),
                        message_type=msg.get("type", "text")
                    ))
            
            # 创建游戏会话
            session = await roleplay_service.start_game_session(
                world_description=world_description,
                character=character,
                summary_text=summary_text,
                last_conversation=messages
            )
            
            if session and session.messages:
                # 返回初始场景
                return session.messages[-1].content, True, ""
            else:
                return None, False, "无法创建游戏会话"
                
        except Exception as e:
            return None, False, f"开始角色扮演时发生错误: {str(e)}"
    
    async def role_play_response(
        self, 
        messages: List[Dict[str, Any]], 
        world_description: str,
        character_description: str,
        temperature: float = 0.7
    ) -> Tuple[str, bool, str]:
        """角色扮演回复"""
        try:
            await self.initialize()
            roleplay_service = self.service_container.get_role_play_service()
            
            # 创建临时会话
            character = CharacterModel(
                name="角色",
                description=character_description,
                world_context=world_description
            )
            
            session = EnhancedGameSession(
                world_description=world_description,
                character=character
            )
            
            # 添加历史消息
            for msg in messages[:-1]:  # 除了最后一条消息
                session.add_message(EnhancedMessage(
                    role=msg.get("role", "user"),
                    content=msg.get("content", "")
                ))
            
            # 处理最后一条用户消息
            if messages:
                last_message = messages[-1]
                response = await roleplay_service.process_user_action(
                    session=session,
                    user_action=last_message.get("content", "")
                )
                
                if response:
                    return response, True, ""
                else:
                    return "", False, "获取回复失败"
            else:
                return "", False, "没有可处理的消息"
                
        except Exception as e:
            return "", False, f"生成回复时发生错误: {str(e)}"
    
    async def save_game(
        self, 
        messages: List[Dict[str, Any]], 
        world_description: str, 
        character_description: str,
        character_name: str = "",
        save_name: Optional[str] = None
    ) -> Tuple[str, bool, str]:
        """保存游戏"""
        try:
            await self.initialize()
            save_manager = self.service_container.get_save_manager()
            
            # 创建游戏会话
            character = CharacterModel(
                name=character_name or "角色",
                description=character_description,
                world_context=world_description
            )
            
            session = EnhancedGameSession(
                world_description=world_description,
                character=character
            )
            
            # 添加消息
            for msg in messages:
                session.add_message(EnhancedMessage(
                    role=msg.get("role", "user"),
                    content=msg.get("content", "")
                ))
            
            # 保存游戏
            save_file = await save_manager.save_game_session(
                session=session,
                save_name=save_name
            )
            
            if save_file:
                return save_file.name, True, "游戏保存成功"
            else:
                return "", False, "游戏保存失败"
                
        except Exception as e:
            return "", False, f"保存游戏时发生错误: {str(e)}"
    
    async def load_game(self, save_name: str) -> Tuple[str, str, str, Optional[List[Dict[str, Any]]], str, bool, str]:
        """加载游戏"""
        try:
            await self.initialize()
            save_loader = self.service_container.get_save_loader_service()
            
            result = save_loader.load_save_by_name(save_name)
            if result:
                session, save_file = result
                
                # 转换消息格式
                last_conversation = []
                for msg in session.messages[-10:]:  # 只返回最近10条消息
                    last_conversation.append({
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
                    })
                
                return (
                    session.world_description,
                    session.summary_text,
                    save_name,
                    last_conversation,
                    session.character.name,
                    True,
                    ""
                )
            else:
                return "", "", "", None, "", False, "存档加载失败"
                
        except Exception as e:
            return "", "", "", None, "", False, f"加载游戏时发生错误: {str(e)}"
    
    async def get_save_list(self) -> Tuple[List[Dict[str, Any]], bool, str]:
        """获取存档列表"""
        try:
            await self.initialize()
            save_manager = self.service_container.get_save_manager()
            
            saves = save_manager.get_save_list()
            return saves, True, ""
            
        except Exception as e:
            return [], False, f"获取存档列表时发生错误: {str(e)}"
    
    async def delete_save(self, save_name: str) -> Tuple[bool, str]:
        """删除存档"""
        try:
            await self.initialize()
            save_manager = self.service_container.get_save_manager()
            
            success = save_manager.delete_save(save_name)
            if success:
                return True, "存档删除成功"
            else:
                return False, "存档删除失败"
                
        except Exception as e:
            return False, f"删除存档时发生错误: {str(e)}"
    
    async def format_ai_response(self, response: str) -> Dict[str, Any]:
        """格式化AI回应"""
        try:
            await self.initialize()
            roleplay_service = self.service_container.get_role_play_service()
            
            return roleplay_service.format_ai_response(response)
            
        except Exception as e:
            return {
                "raw_content": response,
                "formatted_content": response,
                "error": str(e)
            }
    
    async def get_music_status(self) -> Dict[str, Any]:
        """获取音乐播放状态"""
        try:
            await self.initialize()
            music_service = self.service_container.get_music_service()
            
            return music_service.get_music_status()
            
        except Exception as e:
            return {"error": str(e)}
    
    async def play_music_by_mood(self, mood: str) -> Dict[str, Any]:
        """根据情景播放音乐"""
        try:
            await self.initialize()
            music_service = self.service_container.get_music_service()
            
            return music_service.play_music_by_mood(mood)
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

# 创建全局服务实例
wgarp_service = WGARPService()
