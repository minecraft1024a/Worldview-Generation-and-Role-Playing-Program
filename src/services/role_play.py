"""
角色扮演服务
提供游戏对话、场景生成和剧情推进功能
"""

import logging
import re
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from ..core.llm import LLMService
from ..models import GameSession, CharacterModel, GameState, Message
from ..utils.error_handler import ErrorHandler

logger = logging.getLogger(__name__)

class RolePlayService:
    """角色扮演服务类"""
    
    def __init__(self, llm_service: LLMService, error_handler: ErrorHandler):
        self.llm_service = llm_service
        self.error_handler = error_handler
    
    async def start_game_session(
        self, 
        world_description: str,
        character: CharacterModel,
        summary_text: Optional[str] = None,
        last_conversation: Optional[List[Message]] = None
    ) -> Optional[GameSession]:
        """
        开始新的游戏会话
        
        Args:
            world_description: 世界观描述
            character: 角色模型
            summary_text: 之前的游戏摘要
            last_conversation: 最近的对话记录
            
        Returns:
            游戏会话对象，失败时返回None
        """
        try:
            logger.info(f"开始游戏会话，角色: {character.name}")
            
            # 创建游戏会话
            session = GameSession(
                world_description=world_description,
                character=character,
                summary_text=summary_text or "",
                messages=last_conversation or []
            )
            
            # 生成初始场景
            initial_scenario = await self._generate_initial_scenario(
                session, summary_text is not None
            )
            
            if initial_scenario:
                # 添加系统消息
                session.add_message(Message(
                    role="assistant",
                    content=initial_scenario,
                    timestamp=datetime.now(),
                    message_type="scenario"
                ))
                
                logger.info("游戏会话创建成功")
                return session
            else:
                logger.error("无法生成初始场景")
                return None
            
        except Exception as e:
            self.error_handler.handle_error(e, "开始游戏会话")
            return None
    
    async def process_user_action(
        self, 
        session: GameSession, 
        user_action: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        处理用户行动并生成AI回应
        
        Args:
            session: 游戏会话
            user_action: 用户行动描述
            context: 额外上下文信息
            
        Returns:
            AI回应内容，失败时返回None
        """
        try:
            logger.info(f"处理用户行动: {user_action[:50]}...")
            
            # 添加用户消息
            session.add_message(Message(
                role="user",
                content=f"我的行动：{user_action}",
                timestamp=datetime.now(),
                message_type="action"
            ))
            
            # 构建系统提示
            system_prompt = self._build_roleplay_system_prompt(session)
            
            # 准备对话历史
            conversation_history = self._prepare_conversation_history(session)
            
            # 生成AI回应
            ai_response = await self.llm_service.generate_roleplay_response(
                conversation_history=conversation_history,
                system_prompt=system_prompt,
                world_context=session.world_description,
                character_context=session.character.description
            )
            
            if ai_response:
                # 添加AI回应
                session.add_message(Message(
                    role="assistant",
                    content=ai_response,
                    timestamp=datetime.now(),
                    message_type="response"
                ))
                
                # 更新游戏状态
                self._update_game_state(session, user_action, ai_response)
                
                logger.info("成功生成AI回应")
                return ai_response
            else:
                logger.error("AI回应生成失败")
                return None
            
        except Exception as e:
            self.error_handler.handle_error(e, "处理用户行动")
            return None
    
    def format_ai_response(self, response: str) -> Dict[str, Any]:
        """
        格式化AI回应，提取结构化信息
        
        Args:
            response: 原始AI回应
            
        Returns:
            格式化后的回应数据
        """
        try:
            formatted_data = {
                "raw_content": response,
                "formatted_content": "",
                "components": {},
                "user_identity": "",
                "time": "",
                "location": "",
                "scenario": "",
                "user_status": "",
                "user_inventory": "",
                "choices": []
            }
            
            lines = response.split('\n')
            current_section = ""
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 解析不同组件
                if line.startswith('用户身份：'):
                    formatted_data["user_identity"] = line[5:].strip()
                    current_section = f"👤 {line}"
                elif line.startswith('时间:') or line.startswith('时间：'):
                    formatted_data["time"] = line[3:].strip()
                    current_section += f"\n🕐 {line}"
                elif line.startswith('地点:') or line.startswith('地点：'):
                    formatted_data["location"] = line[3:].strip()
                    current_section += f"\n📍 {line}"
                elif line.startswith('情景:') or line.startswith('情景：'):
                    formatted_data["scenario"] = line[3:].strip()
                    current_section += f"\n🎬 {line}"
                elif line.startswith('用户状态:') or line.startswith('用户状态：'):
                    formatted_data["user_status"] = line[5:].strip()
                    current_section += f"\n💪 {line}"
                elif line.startswith('用户物品栏:') or line.startswith('用户物品栏：'):
                    formatted_data["user_inventory"] = line[6:].strip()
                    current_section += f"\n🎒 {line}"
                elif re.match(r'^\d+\.', line):
                    formatted_data["choices"].append(line)
                    current_section += f"\n🔸 {line}"
                elif line == '===============':
                    current_section += f"\n{'─' * 50}"
                else:
                    current_section += f"\n{line}"
            
            formatted_data["formatted_content"] = current_section
            
            return formatted_data
            
        except Exception as e:
            logger.error(f"格式化AI回应失败: {e}")
            return {
                "raw_content": response,
                "formatted_content": response,
                "components": {},
                "error": str(e)
            }
    
    def get_game_statistics(self, session: GameSession) -> Dict[str, Any]:
        """
        获取游戏统计信息
        
        Args:
            session: 游戏会话
            
        Returns:
            统计信息字典
        """
        try:
            stats = {
                "session_duration": 0,
                "total_messages": len(session.messages),
                "user_actions": 0,
                "ai_responses": 0,
                "character_name": session.character.name,
                "game_state": session.game_state.dict() if session.game_state else {},
                "start_time": session.created_at.isoformat(),
                "last_activity": None
            }
            
            # 计算统计数据
            user_actions = 0
            ai_responses = 0
            last_message_time = None
            
            for message in session.messages:
                if message.role == "user":
                    user_actions += 1
                elif message.role == "assistant":
                    ai_responses += 1
                
                if message.timestamp:
                    last_message_time = message.timestamp
            
            stats["user_actions"] = user_actions
            stats["ai_responses"] = ai_responses
            
            if last_message_time:
                stats["last_activity"] = last_message_time.isoformat()
                stats["session_duration"] = int(
                    (last_message_time - session.created_at).total_seconds()
                )
            
            return stats
            
        except Exception as e:
            self.error_handler.handle_error(e, "获取游戏统计")
            return {"error": str(e)}
    
    async def _generate_initial_scenario(
        self, 
        session: GameSession, 
        is_continuation: bool = False
    ) -> Optional[str]:
        """生成初始游戏场景"""
        try:
            if is_continuation and session.summary_text:
                # 继续之前的游戏
                prompt = f"""
                基于以下背景信息继续角色扮演游戏：
                
                世界观：{session.world_description}
                角色：{session.character.description}
                之前的剧情摘要：{session.summary_text}
                
                请生成一个合适的场景，让玩家可以继续之前的冒险。
                """
            else:
                # 全新的游戏
                prompt = f"""
                开始一个全新的角色扮演游戏：
                
                世界观：{session.world_description}
                角色：{session.character.description}
                
                请为这个角色生成一个引人入胜的开场场景。
                """
            
            system_prompt = self._build_roleplay_system_prompt(session)
            
            response = await self.llm_service.generate_text(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
            return response
            
        except Exception as e:
            logger.error(f"生成初始场景失败: {e}")
            return None
    
    def _build_roleplay_system_prompt(self, session: GameSession) -> str:
        """构建角色扮演的系统提示"""
        return f"""
        你是一个角色扮演游戏的主持人（DM）。请严格按照以下格式输出每一轮内容：

        用户身份：
        时间:
        地点:
        情景:
        ===============
        用户状态:
        用户物品栏:
        用户接下来的选择:
        1. [选择1]
        2. [选择2]
        3. [选择3]

        游戏设定：
        - 世界观：{session.world_description}
        - 角色：{session.character.description}
        
        注意事项：
        1. 保持角色一致性和世界观逻辑
        2. 为用户提供有意义的选择
        3. 让故事富有张力和趣味性
        4. 响应用户的行动并推进剧情
        5. 严格按照格式输出，不要添加多余内容
        """
    
    def _prepare_conversation_history(self, session: GameSession) -> List[Dict[str, str]]:
        """准备对话历史，用于LLM调用"""
        history = []
        
        # 取最近的消息，避免超出token限制
        recent_messages = session.messages[-20:] if len(session.messages) > 20 else session.messages
        
        for message in recent_messages:
            history.append({
                "role": message.role,
                "content": message.content
            })
        
        return history
    
    def _update_game_state(self, session: GameSession, user_action: str, ai_response: str):
        """更新游戏状态"""
        try:
            if not session.game_state:
                session.game_state = GameState()
            
            # 提取状态信息
            formatted_response = self.format_ai_response(ai_response)
            
            # 更新位置
            if formatted_response.get("location"):
                session.game_state.current_location = formatted_response["location"]
            
            # 更新时间
            if formatted_response.get("time"):
                session.game_state.game_time = formatted_response["time"]
            
            # 更新状态
            if formatted_response.get("user_status"):
                session.game_state.player_status = formatted_response["user_status"]
            
            # 更新物品栏
            if formatted_response.get("user_inventory"):
                session.game_state.inventory = formatted_response["user_inventory"]
            
            # 增加回合数
            session.game_state.turn_count += 1
            
        except Exception as e:
            logger.error(f"更新游戏状态失败: {e}")
