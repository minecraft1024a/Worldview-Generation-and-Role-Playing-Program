"""
存档加载服务
提供智能存档加载和管理功能
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from ..services.save_manager import SaveManager
from ..models import GameSession, SaveFile, CharacterModel
from ..utils.error_handler import ErrorHandler

logger = logging.getLogger(__name__)

class SaveLoaderService:
    """智能存档加载器服务"""
    
    def __init__(self, save_manager: SaveManager, error_handler: ErrorHandler):
        self.save_manager = save_manager
        self.error_handler = error_handler
    
    def get_saves_summary(self) -> Dict[str, Any]:
        """
        获取存档摘要信息
        
        Returns:
            存档摘要数据
        """
        try:
            saves = self.save_manager.get_save_list()
            
            if not saves:
                return {
                    "total_saves": 0,
                    "saves": [],
                    "message": "未找到任何存档文件",
                    "suggestion": "需要先进行游戏并生成存档"
                }
            
            # 分类统计
            total_saves = len(saves)
            recent_saves = []
            old_saves = []
            
            for save in saves:
                try:
                    last_played = datetime.fromisoformat(save.get("last_played", ""))
                    days_ago = (datetime.now() - last_played).days
                    
                    save_info = {
                        "name": save["name"],
                        "character_name": save["character_name"],
                        "last_played": save["last_played"],
                        "days_ago": days_ago,
                        "message_count": save["message_count"],
                        "world_preview": save["world_description"],
                        "file_size_mb": round(save["file_size"] / 1024 / 1024, 2)
                    }
                    
                    if days_ago <= 7:
                        recent_saves.append(save_info)
                    else:
                        old_saves.append(save_info)
                        
                except Exception as e:
                    logger.warning(f"处理存档信息时出错: {e}")
                    continue
            
            return {
                "total_saves": total_saves,
                "recent_saves": recent_saves,
                "old_saves": old_saves,
                "saves": saves,
                "message": f"找到 {total_saves} 个存档文件"
            }
            
        except Exception as e:
            self.error_handler.handle_error(e, "获取存档摘要")
            return {
                "total_saves": 0,
                "saves": [],
                "error": str(e)
            }
    
    def load_save_by_name(self, save_name: str) -> Optional[Tuple[GameSession, SaveFile]]:
        """
        按名称加载存档
        
        Args:
            save_name: 存档名称
            
        Returns:
            (游戏会话, 存档文件) 元组，失败时返回None
        """
        try:
            logger.info(f"尝试加载存档: {save_name}")
            
            result = self.save_manager.load_game_session(save_name)
            if result:
                session, save_file = result
                logger.info(f"存档加载成功: {save_name}")
                return session, save_file
            else:
                logger.error(f"存档加载失败: {save_name}")
                return None
                
        except Exception as e:
            self.error_handler.handle_error(e, f"加载存档 {save_name}")
            return None
    
    def get_save_preview(self, save_name: str) -> Optional[Dict[str, Any]]:
        """
        获取存档预览信息
        
        Args:
            save_name: 存档名称
            
        Returns:
            存档预览数据
        """
        try:
            details = self.save_manager.get_save_details(save_name)
            if not details:
                return None
            
            # 构建预览信息
            preview = {
                "name": details["name"],
                "character": {
                    "name": details["character"].get("name", "未知角色"),
                    "description_preview": details["character"].get("description", "")[:200] + "..."
                },
                "world_preview": details["world_description"][:300] + "...",
                "summary_preview": details["summary_text"][:200] + "..." if details["summary_text"] else "暂无摘要",
                "statistics": {
                    "created_at": details["created_at"],
                    "last_played": details["last_played"],
                    "message_count": details["message_count"],
                    "file_size_mb": round(details["file_size"] / 1024 / 1024, 2)
                },
                "game_state": details.get("game_state", {}),
                "can_load": True
            }
            
            return preview
            
        except Exception as e:
            self.error_handler.handle_error(e, f"获取存档预览 {save_name}")
            return None
    
    def search_saves(self, query: str) -> List[Dict[str, Any]]:
        """
        搜索存档
        
        Args:
            query: 搜索关键词
            
        Returns:
            匹配的存档列表
        """
        try:
            all_saves = self.save_manager.get_save_list()
            if not all_saves or not query:
                return all_saves
            
            query_lower = query.lower()
            matching_saves = []
            
            for save in all_saves:
                # 在存档名称、角色名称、世界描述中搜索
                if (query_lower in save.get("name", "").lower() or
                    query_lower in save.get("character_name", "").lower() or
                    query_lower in save.get("world_description", "").lower()):
                    matching_saves.append(save)
            
            logger.info(f"搜索 '{query}' 找到 {len(matching_saves)} 个匹配的存档")
            return matching_saves
            
        except Exception as e:
            self.error_handler.handle_error(e, f"搜索存档: {query}")
            return []
    
    def delete_save_by_name(self, save_name: str) -> Dict[str, Any]:
        """
        删除指定存档
        
        Args:
            save_name: 存档名称
            
        Returns:
            删除结果
        """
        try:
            success = self.save_manager.delete_save(save_name)
            
            if success:
                return {
                    "success": True,
                    "message": f"存档 '{save_name}' 删除成功"
                }
            else:
                return {
                    "success": False,
                    "message": f"存档 '{save_name}' 不存在或删除失败"
                }
                
        except Exception as e:
            self.error_handler.handle_error(e, f"删除存档 {save_name}")
            return {
                "success": False,
                "message": f"删除存档时发生错误: {str(e)}"
            }
    
    def backup_save(self, save_name: str, backup_name: Optional[str] = None) -> Dict[str, Any]:
        """
        备份存档
        
        Args:
            save_name: 原存档名称
            backup_name: 备份名称，为空时自动生成
            
        Returns:
            备份结果
        """
        try:
            # 加载原存档
            result = self.save_manager.load_game_session(save_name)
            if not result:
                return {
                    "success": False,
                    "message": f"原存档 '{save_name}' 不存在或无法加载"
                }
            
            session, save_file = result
            
            # 生成备份名称
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{save_name}_backup_{timestamp}"
            
            # 创建备份存档
            backup_result = self.save_manager.save_game_session(
                session=session,
                save_name=backup_name,
                auto_generate_summary=False
            )
            
            if backup_result:
                return {
                    "success": True,
                    "message": f"存档备份成功: {backup_name}",
                    "backup_name": backup_name
                }
            else:
                return {
                    "success": False,
                    "message": "备份过程中发生错误"
                }
                
        except Exception as e:
            self.error_handler.handle_error(e, f"备份存档 {save_name}")
            return {
                "success": False,
                "message": f"备份存档时发生错误: {str(e)}"
            }
    
    def get_save_statistics(self) -> Dict[str, Any]:
        """
        获取存档统计信息
        
        Returns:
            存档统计数据
        """
        try:
            saves = self.save_manager.get_save_list()
            
            if not saves:
                return {
                    "total_saves": 0,
                    "total_size_mb": 0,
                    "characters": [],
                    "oldest_save": None,
                    "newest_save": None
                }
            
            # 统计数据
            total_size = sum(save.get("file_size", 0) for save in saves)
            characters = list(set(save.get("character_name", "未知") for save in saves))
            
            # 最旧和最新的存档
            saves_by_date = sorted(saves, key=lambda x: x.get("created_at", ""))
            oldest_save = saves_by_date[0] if saves_by_date else None
            newest_save = saves_by_date[-1] if saves_by_date else None
            
            return {
                "total_saves": len(saves),
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "unique_characters": len(characters),
                "characters": characters,
                "oldest_save": {
                    "name": oldest_save["name"],
                    "created_at": oldest_save["created_at"]
                } if oldest_save else None,
                "newest_save": {
                    "name": newest_save["name"],
                    "created_at": newest_save["created_at"]
                } if newest_save else None
            }
            
        except Exception as e:
            self.error_handler.handle_error(e, "获取存档统计")
            return {"error": str(e)}
    
    def clean_old_saves(self, days_threshold: int = 30) -> Dict[str, Any]:
        """
        清理旧存档
        
        Args:
            days_threshold: 天数阈值，超过这个天数的存档将被标记为可清理
            
        Returns:
            清理建议
        """
        try:
            saves = self.save_manager.get_save_list()
            old_saves = []
            
            for save in saves:
                try:
                    last_played = datetime.fromisoformat(save.get("last_played", ""))
                    days_ago = (datetime.now() - last_played).days
                    
                    if days_ago > days_threshold:
                        old_saves.append({
                            "name": save["name"],
                            "days_ago": days_ago,
                            "file_size_mb": round(save["file_size"] / 1024 / 1024, 2)
                        })
                except Exception:
                    continue
            
            total_old_size = sum(save["file_size_mb"] for save in old_saves)
            
            return {
                "old_saves_count": len(old_saves),
                "old_saves": old_saves,
                "total_old_size_mb": round(total_old_size, 2),
                "days_threshold": days_threshold,
                "suggestion": f"发现 {len(old_saves)} 个超过 {days_threshold} 天未玩的存档，共占用 {total_old_size:.2f} MB 空间"
            }
            
        except Exception as e:
            self.error_handler.handle_error(e, "清理旧存档分析")
            return {"error": str(e)}
