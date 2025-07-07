from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import json
import uuid
from datetime import datetime
from app.services.wgarp_service import wgarp_service


class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.game_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket) -> str:
        """建立 WebSocket 连接"""
        await websocket.accept()
        session_id = str(uuid.uuid4())
        self.active_connections[session_id] = websocket
        return session_id
    
    def disconnect(self, session_id: str):
        """断开连接"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.game_sessions:
            del self.game_sessions[session_id]
    
    async def send_message(self, session_id: str, message: dict):
        """发送消息到特定连接"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                await websocket.send_text(json.dumps(message))
            except:
                self.disconnect(session_id)
    
    def create_game_session(self, session_id: str, world_description: str, save_name: str = None):
        """创建游戏会话"""
        self.game_sessions[session_id] = {
            "world_description": world_description,
            "messages": [],
            "save_name": save_name,
            "role": "",
            "created_at": datetime.now(),
            "last_updated": datetime.now()
        }
    
    def add_message(self, session_id: str, role: str, content: str):
        """添加消息到会话"""
        if session_id in self.game_sessions:
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            self.game_sessions[session_id]["messages"].append(message)
            self.game_sessions[session_id]["last_updated"] = datetime.now()
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """获取游戏会话"""
        return self.game_sessions.get(session_id, {})


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端点处理函数"""
    session_id = await manager.connect(websocket)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get("type")
            
            if message_type == "start_game":
                # 开始新游戏
                world_description = message_data.get("world_description", "")
                save_name = message_data.get("save_name")
                manager.create_game_session(session_id, world_description, save_name)
                
                await manager.send_message(session_id, {
                    "type": "game_started",
                    "session_id": session_id,
                    "world_description": world_description
                })
            
            elif message_type == "load_game":
                # 加载游戏
                save_name = message_data.get("save_name")
                world_desc, summary, _, last_conversation, role, success, error_msg = wgarp_service.load_game(save_name)
                
                if success:
                    manager.create_game_session(session_id, world_desc, save_name)
                    session = manager.get_session(session_id)
                    session["role"] = role
                    
                    # 如果有最后对话，添加到消息列表
                    if last_conversation:
                        manager.add_message(session_id, last_conversation.get("role", "assistant"), 
                                          last_conversation.get("content", ""))
                    
                    await manager.send_message(session_id, {
                        "type": "game_loaded",
                        "session_id": session_id,
                        "world_description": world_desc,
                        "summary": summary,
                        "role": role,
                        "last_conversation": last_conversation
                    })
                else:
                    await manager.send_message(session_id, {
                        "type": "error",
                        "message": error_msg
                    })
            
            elif message_type == "player_action":
                # 玩家行动
                action = message_data.get("content", "")
                session = manager.get_session(session_id)
                
                if session:
                    # 添加玩家消息
                    manager.add_message(session_id, "user", action)
                    
                    # 获取AI回复
                    messages = session["messages"]
                    response, success, error_msg = wgarp_service.role_play_response(messages)
                    
                    if success:
                        # 添加AI回复
                        manager.add_message(session_id, "assistant", response)
                        
                        await manager.send_message(session_id, {
                            "type": "ai_response",
                            "content": response,
                            "timestamp": datetime.now().isoformat()
                        })
                    else:
                        await manager.send_message(session_id, {
                            "type": "error",
                            "message": error_msg
                        })
            
            elif message_type == "save_game":
                # 保存游戏
                session = manager.get_session(session_id)
                if session:
                    save_name, success, message = wgarp_service.save_game(
                        session["messages"],
                        session["world_description"],
                        session.get("save_name"),
                        session.get("role", "")
                    )
                    
                    if success:
                        session["save_name"] = save_name
                        await manager.send_message(session_id, {
                            "type": "game_saved",
                            "save_name": save_name,
                            "message": message
                        })
                    else:
                        await manager.send_message(session_id, {
                            "type": "error",
                            "message": message
                        })
            
            elif message_type == "ping":
                # 心跳检测
                await manager.send_message(session_id, {
                    "type": "pong"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        await manager.send_message(session_id, {
            "type": "error",
            "message": f"服务器错误: {str(e)}"
        })
        manager.disconnect(session_id)
