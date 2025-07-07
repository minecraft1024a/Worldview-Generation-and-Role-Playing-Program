import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.config_manager import config_manager
from src.llm_core import llm_core
from src.summary import save_manager
from src.load_summary import save_loader
from src.error_handler import error_handler
import json
import random
from typing import List, Optional, Dict, Any
from datetime import datetime


class WGARPService:
    """WGARP 服务类，封装所有核心业务逻辑"""
    
    def __init__(self):
        self.config_manager = config_manager
        self.llm_core = llm_core
        self.save_manager = save_manager
        self.save_loader = save_loader
        self.error_handler = error_handler
        
    def get_daily_quote(self) -> str:
        """获取每日格言"""
        try:
            quotes_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src', 'daily_quotes.json')
            with open(quotes_path, "r", encoding="utf-8") as file:
                quotes = json.load(file).get("quotes", [])
            return random.choice(quotes) if quotes else "今日无名言，明日再试！"
        except Exception:
            return "欢迎来到WGARP世界！"
    
    def generate_world(self, background: str) -> tuple[str, bool, str]:
        """生成世界观"""
        try:
            world_desc = self.llm_core.generate_world(background)
            if world_desc:
                return world_desc, True, ""
            else:
                return "", False, "世界观生成失败"
        except Exception as e:
            self.error_handler.handle_llm_error(e)
            return "", False, f"生成世界观时发生错误: {str(e)}"
    
    def generate_character(self, world_description: str, prompt: str) -> tuple[str, bool, str]:
        """生成角色"""
        try:
            character = self.llm_core.generate_character(world_description, prompt)
            if character:
                return character, True, ""
            else:
                return "", False, "角色生成失败"
        except Exception as e:
            self.error_handler.handle_llm_error(e)
            return "", False, f"生成角色时发生错误: {str(e)}"
    
    def role_play_response(self, messages: List[Dict[str, Any]], temperature: float = 0.7) -> tuple[str, bool, str]:
        """角色扮演回复"""
        try:
            # 转换消息格式
            formatted_messages = [{"role": msg["role"], "content": msg["content"]} for msg in messages]
            response = self.llm_core.role_play_response(formatted_messages, temperature)
            if response:
                return response, True, ""
            else:
                return "", False, "获取回复失败"
        except Exception as e:
            self.error_handler.handle_llm_error(e)
            return "", False, f"生成回复时发生错误: {str(e)}"
    
    def save_game(self, messages: List[Dict[str, Any]], world_description: str, 
                  save_name: Optional[str] = None, role: Optional[str] = None) -> tuple[str, bool, str]:
        """保存游戏"""
        try:
            # 转换消息格式
            formatted_messages = [{"role": msg["role"], "content": msg["content"]} for msg in messages]
            result_save_name = self.save_manager.save_game_state(
                formatted_messages, world_description, save_name, role
            )
            if result_save_name:
                return result_save_name, True, "游戏保存成功"
            else:
                return "", False, "游戏保存失败"
        except Exception as e:
            self.error_handler.handle_llm_error(e)
            return "", False, f"保存游戏时发生错误: {str(e)}"
    
    def load_game(self, save_name: str) -> tuple[str, str, str, Optional[Dict[str, Any]], str, bool, str]:
        """加载游戏"""
        try:
            result = self.save_manager.load_game_state(save_name)
            if result and len(result) >= 5:
                world_desc, summary, _, last_conversation, role = result
                return world_desc, summary, save_name, last_conversation, role, True, ""
            else:
                return "", "", "", None, "", False, "存档加载失败"
        except Exception as e:
            self.error_handler.handle_llm_error(e)
            return "", "", "", None, "", False, f"加载游戏时发生错误: {str(e)}"
    
    def get_save_list(self) -> tuple[List[Dict[str, Any]], bool, str]:
        """获取存档列表"""
        try:
            saves = self.save_manager.get_save_list()
            return saves, True, ""
        except Exception as e:
            self.error_handler.handle_llm_error(e)
            return [], False, f"获取存档列表时发生错误: {str(e)}"
    
    def delete_save(self, save_name: str) -> tuple[bool, str]:
        """删除存档"""
        try:
            success = self.save_manager.delete_save(save_name)
            if success:
                return True, "存档删除成功"
            else:
                return False, "存档删除失败"
        except Exception as e:
            self.error_handler.handle_llm_error(e)
            return False, f"删除存档时发生错误: {str(e)}"


# 创建全局服务实例
wgarp_service = WGARPService()
