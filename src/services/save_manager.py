"""
存档管理服务
提供游戏存档的保存、加载、管理和摘要生成功能
"""

import json
import os
import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path

from ..core.llm import LLMService
from ..models import GameSession, SaveFile, Message
from ..utils.error_handler import ErrorHandler

logger = logging.getLogger(__name__)

class SaveManager:
    """智能存档管理器"""
    
    def __init__(self, llm_service: LLMService, error_handler: ErrorHandler, data_dir: str = "data"):
        self.llm_service = llm_service
        self.error_handler = error_handler
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
    
    async def save_game_session(
        self, 
        session: GameSession, 
        save_name: Optional[str] = None,
        auto_generate_summary: bool = True
    ) -> Optional[SaveFile]:
        """
        保存游戏会话
        
        Args:
            session: 游戏会话对象
            save_name: 存档名称，为空时自动生成
            auto_generate_summary: 是否自动生成摘要
            
        Returns:
            存档文件对象，失败时返回None
        """
        try:
            # 生成存档名称
            if not save_name:
                save_name = self._generate_save_name(session)
            
            logger.info(f"开始保存游戏会话: {save_name}")
            
            # 生成智能摘要
            summary_text = ""
            if auto_generate_summary and session.messages:
                summary_text = await self._generate_smart_summary(session)
            
            # 创建存档对象
            save_file = SaveFile(
                name=save_name,
                world_description=session.world_description,
                character=session.character,
                summary_text=summary_text,
                messages=self._compress_messages(session.messages),
                game_state=session.game_state,
                created_at=datetime.now(),
                last_played=datetime.now()
            )
            
            # 保存到文件
            save_path = self.data_dir / f"{save_name}.json"
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_file.dict(), f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"游戏会话保存成功: {save_path}")
            return save_file
            
        except Exception as e:
            self.error_handler.handle_error(e, "保存游戏会话")
            return None
    
    def load_game_session(self, save_name: str) -> Optional[Tuple[GameSession, SaveFile]]:
        """
        加载游戏会话
        
        Args:
            save_name: 存档名称
            
        Returns:
            (游戏会话对象, 存档文件对象) 元组，失败时返回None
        """
        try:
            logger.info(f"开始加载游戏会话: {save_name}")
            
            save_path = self.data_dir / f"{save_name}.json"
            if not save_path.exists():
                logger.error(f"存档文件不存在: {save_path}")
                return None
            
            # 读取存档文件
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # 创建存档对象
            save_file = SaveFile(**save_data)
            
            # 重建游戏会话
            session = GameSession(
                world_description=save_file.world_description,
                character=save_file.character,
                summary_text=save_file.summary_text,
                messages=self._decompress_messages(save_file.messages),
                game_state=save_file.game_state
            )
            
            # 更新最后游玩时间
            save_file.last_played = datetime.now()
            self._update_save_file(save_file)
            
            logger.info(f"游戏会话加载成功: {save_name}")
            return session, save_file
            
        except Exception as e:
            self.error_handler.handle_error(e, "加载游戏会话")
            return None
    
    def get_save_list(self) -> List[Dict[str, Any]]:
        """
        获取所有存档的列表
        
        Returns:
            存档信息列表
        """
        try:
            saves = []
            
            for save_file in self.data_dir.glob("*.json"):
                try:
                    with open(save_file, 'r', encoding='utf-8') as f:
                        save_data = json.load(f)
                    
                    save_info = {
                        "name": save_data.get("name", save_file.stem),
                        "character_name": save_data.get("character", {}).get("name", "未知角色"),
                        "created_at": save_data.get("created_at", ""),
                        "last_played": save_data.get("last_played", ""),
                        "message_count": len(save_data.get("messages", [])),
                        "world_description": save_data.get("world_description", "")[:100] + "...",
                        "file_size": save_file.stat().st_size,
                        "file_path": str(save_file)
                    }
                    
                    saves.append(save_info)
                    
                except Exception as e:
                    logger.warning(f"读取存档文件失败: {save_file}, 错误: {e}")
                    continue
            
            # 按最后游玩时间排序
            saves.sort(key=lambda x: x.get("last_played", ""), reverse=True)
            
            logger.info(f"找到 {len(saves)} 个存档文件")
            return saves
            
        except Exception as e:
            self.error_handler.handle_error(e, "获取存档列表")
            return []
    
    def delete_save(self, save_name: str) -> bool:
        """
        删除存档
        
        Args:
            save_name: 存档名称
            
        Returns:
            删除是否成功
        """
        try:
            save_path = self.data_dir / f"{save_name}.json"
            if save_path.exists():
                save_path.unlink()
                logger.info(f"存档删除成功: {save_name}")
                return True
            else:
                logger.warning(f"存档文件不存在: {save_name}")
                return False
                
        except Exception as e:
            self.error_handler.handle_error(e, "删除存档")
            return False
    
    def get_save_details(self, save_name: str) -> Optional[Dict[str, Any]]:
        """
        获取存档详细信息
        
        Args:
            save_name: 存档名称
            
        Returns:
            存档详细信息字典
        """
        try:
            save_path = self.data_dir / f"{save_name}.json"
            if not save_path.exists():
                return None
            
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            details = {
                "name": save_data.get("name"),
                "world_description": save_data.get("world_description"),
                "character": save_data.get("character"),
                "summary_text": save_data.get("summary_text"),
                "created_at": save_data.get("created_at"),
                "last_played": save_data.get("last_played"),
                "message_count": len(save_data.get("messages", [])),
                "game_state": save_data.get("game_state"),
                "file_size": save_path.stat().st_size
            }
            
            return details
            
        except Exception as e:
            self.error_handler.handle_error(e, "获取存档详情")
            return None
    
    async def _generate_smart_summary(self, session: GameSession) -> str:
        """生成智能增量摘要"""
        try:
            # 获取最近的对话
            recent_messages = session.messages[-10:] if len(session.messages) > 10 else session.messages
            
            if not recent_messages:
                return ""
            
            # 构建摘要提示
            conversation_text = "\n".join([
                f"{msg.role}: {msg.content}" for msg in recent_messages
            ])
            
            prompt = f"""
            请为以下角色扮演游戏对话生成简洁的剧情摘要：
            
            世界观：{session.world_description}
            角色：{session.character.name}
            
            最近的对话：
            {conversation_text}
            
            请生成一个200字以内的摘要，包含：
            1. 当前剧情进展
            2. 角色状态
            3. 重要事件
            4. 下一步可能的发展
            """
            
            summary = await self.llm_service.generate_text(
                prompt=prompt,
                system_prompt="你是一个专业的游戏剧情摘要生成器，能够准确提取关键信息。"
            )
            
            return summary or ""
            
        except Exception as e:
            logger.error(f"生成智能摘要失败: {e}")
            return ""
    
    def _compress_messages(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """压缩消息格式，减少存储空间"""
        compressed = []
        
        # 只保留最近的20条消息
        recent_messages = messages[-20:] if len(messages) > 20 else messages
        
        for msg in recent_messages:
            compressed_msg = {
                "r": msg.role,
                "c": self._extract_core_content(msg.content),
                "t": msg.timestamp.isoformat() if msg.timestamp else None,
                "type": msg.message_type
            }
            compressed.append(compressed_msg)
        
        return compressed
    
    def _decompress_messages(self, compressed_messages: List[Dict[str, Any]]) -> List[Message]:
        """解压缩消息"""
        messages = []
        
        for compressed in compressed_messages:
            message = Message(
                role=compressed.get("r", "user"),
                content=compressed.get("c", ""),
                timestamp=datetime.fromisoformat(compressed["t"]) if compressed.get("t") else datetime.now(),
                message_type=compressed.get("type", "text")
            )
            messages.append(message)
        
        return messages
    
    def _extract_core_content(self, content: str) -> str:
        """从内容中提取核心信息"""
        # 移除音乐播放和系统提示信息
        lines = content.split('\n')
        filtered_lines = []
        
        for line in lines:
            if not any(keyword in line for keyword in ['🎵', '正在播放', '💾', '摘要生成']):
                filtered_lines.append(line)
        
        core_content = '\n'.join(filtered_lines).strip()
        
        # 限制长度
        if len(core_content) > 800:
            core_content = core_content[:800] + "..."
        
        return core_content
    
    def _generate_save_name(self, session: GameSession) -> str:
        """自动生成存档名称"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        character_name = session.character.name.replace(" ", "_")
        return f"{character_name}_{timestamp}"
    
    def _update_save_file(self, save_file: SaveFile):
        """更新存档文件"""
        try:
            save_path = self.data_dir / f"{save_file.name}.json"
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_file.dict(), f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logger.error(f"更新存档文件失败: {e}")

# 为了保持兼容性，创建一个全局实例
save_manager = None

def get_save_manager(llm_service: LLMService, error_handler: ErrorHandler) -> SaveManager:
    """获取存档管理器实例"""
    global save_manager
    if save_manager is None:
        save_manager = SaveManager(llm_service, error_handler)
    return save_manager
