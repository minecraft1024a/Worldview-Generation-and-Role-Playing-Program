from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class MessageModel(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None


class WorldGenerationRequest(BaseModel):
    background: str = "地理、历史、文化、魔法体系"


class WorldGenerationResponse(BaseModel):
    world_description: str
    success: bool
    message: str = ""


class SaveGameRequest(BaseModel):
    messages: List[MessageModel]
    world_description: str
    save_name: Optional[str] = None
    role: Optional[str] = None


class SaveGameResponse(BaseModel):
    success: bool
    save_name: str
    message: str = ""


class LoadGameResponse(BaseModel):
    success: bool
    world_description: str = ""
    summary: str = ""
    save_name: str = ""
    last_conversation: Optional[MessageModel] = None
    role: str = ""
    message: str = ""


class SaveInfo(BaseModel):
    filename: str
    last_updated: str
    summary_preview: str


class SaveListResponse(BaseModel):
    saves: List[SaveInfo]
    success: bool
    message: str = ""


class RolePlayRequest(BaseModel):
    messages: List[MessageModel]
    world_description: Optional[str] = None
    temperature: float = 0.7


class RolePlayResponse(BaseModel):
    response: str
    success: bool
    message: str = ""


class CharacterGenerationRequest(BaseModel):
    world_description: str
    prompt: str


class CharacterGenerationResponse(BaseModel):
    character: str
    success: bool
    message: str = ""


class DailyQuoteResponse(BaseModel):
    quote: str
    success: bool


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_type: str = "general"


class GameSession(BaseModel):
    session_id: str
    world_description: str
    messages: List[MessageModel]
    save_name: Optional[str] = None
    role: Optional[str] = None
    created_at: datetime
    last_updated: datetime
