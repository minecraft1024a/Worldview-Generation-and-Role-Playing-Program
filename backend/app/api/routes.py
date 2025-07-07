from fastapi import APIRouter, HTTPException
from app.models import (
    DailyQuoteResponse, WorldGenerationRequest, WorldGenerationResponse,
    SaveGameRequest, SaveGameResponse, LoadGameResponse, SaveListResponse,
    RolePlayRequest, RolePlayResponse, CharacterGenerationRequest, 
    CharacterGenerationResponse, ErrorResponse
)
from app.services.wgarp_service import wgarp_service
from typing import List

router = APIRouter()


@router.get("/daily-quote", response_model=DailyQuoteResponse)
async def get_daily_quote():
    """获取每日格言"""
    try:
        quote = wgarp_service.get_daily_quote()
        return DailyQuoteResponse(quote=quote, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-world", response_model=WorldGenerationResponse)
async def generate_world(request: WorldGenerationRequest):
    """生成世界观"""
    try:
        world_desc, success, message = wgarp_service.generate_world(request.background)
        return WorldGenerationResponse(
            world_description=world_desc,
            success=success,
            message=message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-character", response_model=CharacterGenerationResponse)
async def generate_character(request: CharacterGenerationRequest):
    """生成角色"""
    try:
        character, success, message = wgarp_service.generate_character(
            request.world_description, request.prompt
        )
        return CharacterGenerationResponse(
            character=character,
            success=success,
            message=message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/role-play", response_model=RolePlayResponse)
async def role_play(request: RolePlayRequest):
    """角色扮演回复"""
    try:
        messages_dict = [msg.dict() for msg in request.messages]
        response, success, message = wgarp_service.role_play_response(
            messages_dict, request.temperature
        )
        return RolePlayResponse(
            response=response,
            success=success,
            message=message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save-game", response_model=SaveGameResponse)
async def save_game(request: SaveGameRequest):
    """保存游戏"""
    try:
        messages_dict = [msg.dict() for msg in request.messages]
        save_name, success, message = wgarp_service.save_game(
            messages_dict, request.world_description, request.save_name, request.role
        )
        return SaveGameResponse(
            success=success,
            save_name=save_name,
            message=message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/load-game/{save_name}", response_model=LoadGameResponse)
async def load_game(save_name: str):
    """加载游戏"""
    try:
        world_desc, summary, loaded_save_name, last_conversation, role, success, message = wgarp_service.load_game(save_name)
        return LoadGameResponse(
            success=success,
            world_description=world_desc,
            summary=summary,
            save_name=loaded_save_name,
            last_conversation=last_conversation,
            role=role,
            message=message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/saves", response_model=SaveListResponse)
async def get_saves():
    """获取存档列表"""
    try:
        saves, success, message = wgarp_service.get_save_list()
        return SaveListResponse(
            saves=saves,
            success=success,
            message=message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/saves/{save_name}")
async def delete_save(save_name: str):
    """删除存档"""
    try:
        success, message = wgarp_service.delete_save(save_name)
        if success:
            return {"success": True, "message": message}
        else:
            raise HTTPException(status_code=400, detail=message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
