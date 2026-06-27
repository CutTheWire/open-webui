from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from open_webui.utils.auth import get_verified_user
from open_webui.models.character_chat import Characters, CharacterModel, CharacterCreateRequest

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[CharacterModel])
async def get_all_characters(user=Depends(get_verified_user)):
    return await Characters.get_all_characters()


@router.get("/{character_id}", response_model=CharacterModel)
async def get_character(character_id: str, user=Depends(get_verified_user)):
    character = await Characters.get_character_by_id(character_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


@router.post("/", response_model=CharacterModel)
async def create_character(request: CharacterCreateRequest, user=Depends(get_verified_user)):
    author_name = user.name if hasattr(user, 'name') and user.name else "사용자"
    new_char = await Characters.insert_new_character(author_name, request)
    if new_char is None:
        raise HTTPException(status_code=500, detail="Failed to create character")
    return new_char
