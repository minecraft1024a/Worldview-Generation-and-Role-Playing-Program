"""
WGARP 数据模型定义
定义游戏中使用的所有数据结构
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class MessageRole(Enum):
    """消息角色枚举"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class GameState(Enum):
    """游戏状态枚举"""
    IDLE = "idle"
    CREATING_WORLD = "creating_world"
    GENERATING_CHARACTER = "generating_character"
    PLAYING = "playing"
    SAVING = "saving"
    LOADING = "loading"


@dataclass
class Message:
    """游戏消息"""
    role: MessageRole
    content: str
    timestamp: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """从字典创建"""
        timestamp = None
        if data.get("timestamp"):
            timestamp = datetime.fromisoformat(data["timestamp"])
        
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=timestamp,
            metadata=data.get("metadata", {})
        )


@dataclass
class WorldDescription:
    """世界观描述"""
    content: str
    background_prompt: str = ""
    generated_at: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "content": self.content,
            "background_prompt": self.background_prompt,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorldDescription':
        """从字典创建"""
        generated_at = None
        if data.get("generated_at"):
            generated_at = datetime.fromisoformat(data["generated_at"])
        
        return cls(
            content=data["content"],
            background_prompt=data.get("background_prompt", ""),
            generated_at=generated_at,
            metadata=data.get("metadata", {})
        )


@dataclass
class Character:
    """角色信息"""
    name: str = ""
    profession: str = ""
    gender: str = ""
    age: str = ""
    abilities: str = ""
    description: str = ""
    relationships: str = ""
    prompt: str = ""
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "profession": self.profession,
            "gender": self.gender,
            "age": self.age,
            "abilities": self.abilities,
            "description": self.description,
            "relationships": self.relationships,
            "prompt": self.prompt,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        """从字典创建"""
        created_at = None
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"])
        
        return cls(**{k: v for k, v in data.items() if k != "created_at"}, created_at=created_at)
    
    @classmethod
    def from_text(cls, text: str, prompt: str = "") -> 'Character':
        """从文本解析角色信息"""
        character = cls(prompt=prompt)
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('姓名:') or line.startswith('姓名：'):
                character.name = line.split(':', 1)[-1].split('：', 1)[-1].strip()
            elif line.startswith('职业:') or line.startswith('职业：'):
                character.profession = line.split(':', 1)[-1].split('：', 1)[-1].strip()
            elif line.startswith('性别:') or line.startswith('性别：'):
                character.gender = line.split(':', 1)[-1].split('：', 1)[-1].strip()
            elif line.startswith('年龄:') or line.startswith('年龄：'):
                character.age = line.split(':', 1)[-1].split('：', 1)[-1].strip()
            elif line.startswith('能力:') or line.startswith('能力：'):
                character.abilities = line.split(':', 1)[-1].split('：', 1)[-1].strip()
            elif line.startswith('人物具体介绍:') or line.startswith('人物具体介绍：'):
                character.description = line.split(':', 1)[-1].split('：', 1)[-1].strip()
            elif line.startswith('关系:') or line.startswith('关系：'):
                character.relationships = line.split(':', 1)[-1].split('：', 1)[-1].strip()
        
        return character


@dataclass
class GameSession:
    """游戏会话"""
    session_id: str
    world_description: WorldDescription
    character: Optional[Character] = None
    messages: List[Message] = None
    state: GameState = GameState.IDLE
    save_name: Optional[str] = None
    created_at: datetime = None
    last_updated: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.messages is None:
            self.messages = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_updated is None:
            self.last_updated = datetime.now()
        if self.metadata is None:
            self.metadata = {}
    
    def add_message(self, role: MessageRole, content: str, metadata: Dict[str, Any] = None):
        """添加消息"""
        message = Message(role=role, content=content, metadata=metadata or {})
        self.messages.append(message)
        self.last_updated = datetime.now()
    
    def get_recent_messages(self, count: int = 10) -> List[Message]:
        """获取最近的消息"""
        return self.messages[-count:] if len(self.messages) > count else self.messages
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "world_description": self.world_description.to_dict(),
            "character": self.character.to_dict() if self.character else None,
            "messages": [msg.to_dict() for msg in self.messages],
            "state": self.state.value,
            "save_name": self.save_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "metadata": self.metadata
        }


@dataclass
class SaveInfo:
    """存档信息"""
    filename: str
    save_name: str
    last_updated: datetime
    summary_preview: str
    world_preview: str = ""
    character_name: str = ""
    message_count: int = 0
    file_size: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "filename": self.filename,
            "save_name": self.save_name,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "summary_preview": self.summary_preview,
            "world_preview": self.world_preview,
            "character_name": self.character_name,
            "message_count": self.message_count,
            "file_size": self.file_size
        }


@dataclass
class APIResponse:
    """API 响应"""
    success: bool
    data: Any = None
    message: str = ""
    error_code: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "success": self.success,
            "message": self.message
        }
        if self.data is not None:
            result["data"] = self.data
        if self.error_code:
            result["error_code"] = self.error_code
        return result


# 添加扩展的数据模型以支持新的服务架构

@dataclass
class CharacterModel:
    """角色模型（新版本，与Character兼容）"""
    name: str = ""
    description: str = ""
    world_context: str = ""
    creation_prompt: str = ""
    preferences: Dict[str, Any] = None
    modification_history: List[Dict[str, Any]] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {}
        if self.modification_history is None:
            self.modification_history = []
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "world_context": self.world_context,
            "creation_prompt": self.creation_prompt,
            "preferences": self.preferences,
            "modification_history": self.modification_history,
            "created_at": self.created_at.isoformat()
        }
    
    def dict(self) -> Dict[str, Any]:
        """兼容Pydantic风格的方法"""
        return self.to_dict()
    
    @classmethod
    def from_character(cls, character: Character) -> 'CharacterModel':
        """从旧版Character创建"""
        return cls(
            name=character.name,
            description=character.description,
            world_context="",
            creation_prompt=character.prompt,
            created_at=character.created_at
        )


@dataclass
class GameStateModel:
    """游戏状态模型"""
    current_location: str = ""
    player_status: str = ""
    inventory: str = ""
    game_time: str = ""
    turn_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_location": self.current_location,
            "player_status": self.player_status,
            "inventory": self.inventory,
            "game_time": self.game_time,
            "turn_count": self.turn_count
        }
    
    def dict(self) -> Dict[str, Any]:
        """兼容Pydantic风格的方法"""
        return self.to_dict()


@dataclass
class EnhancedMessage:
    """增强的消息模型"""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: Optional[datetime] = None
    message_type: str = "text"  # "text", "action", "scenario", "response"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "message_type": self.message_type,
            "metadata": self.metadata
        }
    
    def dict(self) -> Dict[str, Any]:
        """兼容Pydantic风格的方法"""
        return self.to_dict()
    
    @classmethod
    def from_message(cls, message: Message) -> 'EnhancedMessage':
        """从旧版Message创建"""
        return cls(
            role=message.role.value,
            content=message.content,
            timestamp=message.timestamp,
            metadata=message.metadata
        )


@dataclass 
class EnhancedGameSession:
    """增强的游戏会话模型"""
    world_description: str
    character: CharacterModel
    summary_text: str = ""
    messages: List[EnhancedMessage] = None
    game_state: Optional[GameStateModel] = None
    created_at: datetime = None
    last_activity: Optional[datetime] = None
    
    def __post_init__(self):
        if self.messages is None:
            self.messages = []
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def add_message(self, message: EnhancedMessage):
        """添加消息到会话"""
        self.messages.append(message)
        self.last_activity = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_description": self.world_description,
            "character": self.character.to_dict(),
            "summary_text": self.summary_text,
            "messages": [msg.to_dict() for msg in self.messages],
            "game_state": self.game_state.to_dict() if self.game_state else None,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }
    
    def dict(self) -> Dict[str, Any]:
        """兼容Pydantic风格的方法"""
        return self.to_dict()


@dataclass
class SaveFile:
    """存档文件模型"""
    name: str
    world_description: str
    character: CharacterModel
    summary_text: str = ""
    messages: List[Dict[str, Any]] = None  # 压缩格式的消息
    game_state: Optional[GameStateModel] = None
    created_at: datetime = None
    last_played: datetime = None
    version: str = "1.0"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.messages is None:
            self.messages = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_played is None:
            self.last_played = datetime.now()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "world_description": self.world_description,
            "character": self.character.to_dict(),
            "summary_text": self.summary_text,
            "messages": self.messages,
            "game_state": self.game_state.to_dict() if self.game_state else None,
            "created_at": self.created_at.isoformat(),
            "last_played": self.last_played.isoformat(),
            "version": self.version,
            "metadata": self.metadata
        }
    
    def dict(self) -> Dict[str, Any]:
        """兼容Pydantic风格的方法"""
        return self.to_dict()


@dataclass
class WorldConfig:
    """世界观配置模型"""
    theme: str = ""
    style: str = ""
    complexity: str = ""
    language: str = "中文"
    custom_elements: List[str] = None
    
    def __post_init__(self):
        if self.custom_elements is None:
            self.custom_elements = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "theme": self.theme,
            "style": self.style,
            "complexity": self.complexity,
            "language": self.language,
            "custom_elements": self.custom_elements
        }
    
    def dict(self) -> Dict[str, Any]:
        """兼容Pydantic风格的方法"""
        return self.to_dict()
