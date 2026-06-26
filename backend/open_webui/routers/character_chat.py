from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Optional, List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from open_webui.constants import ERROR_MESSAGES
from open_webui.env import DATA_DIR
from open_webui.utils.auth import get_verified_user

log = logging.getLogger(__name__)

router = APIRouter()

CHARACTERS_JSON_PATH = Path(DATA_DIR) / "character_chats.json"


class Character(BaseModel):
    id: str
    type: str  # "character" or "story"
    name: str
    author: str
    views: str
    rank: int
    imageUrl: str
    # Character specific
    gender: str = ""
    age: str = ""
    details: str = ""
    # Story specific
    prompt: str = ""

class CharacterCreateRequest(BaseModel):
    type: str = "character"
    name: str
    imageUrl: str
    gender: str = ""
    age: str = ""
    details: str = ""
    prompt: str = ""


def load_characters() -> List[dict]:
    if not CHARACTERS_JSON_PATH.exists():
        save_characters([])
        return []
    try:
        with open(CHARACTERS_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log.error(f"Failed to load characters: {e}")
        return []

def save_characters(data: List[dict]):
    try:
        with open(CHARACTERS_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log.error(f"Failed to save characters: {e}")

@router.get("/", response_model=List[Character])
async def get_all_characters(user=Depends(get_verified_user)):
    return load_characters()

@router.get("/{character_id}", response_model=Character)
async def get_character(character_id: str, user=Depends(get_verified_user)):
    characters = load_characters()
    for c in characters:
        if c["id"] == character_id:
            return c
    raise HTTPException(status_code=404, detail="Character not found")

@router.post("/", response_model=Character)
async def create_character(request: CharacterCreateRequest, user=Depends(get_verified_user)):
    characters = load_characters()
    
    # rank 계산
    rank = len(characters) + 1
    
    new_char = {
        "id": str(uuid4()),
        "name": request.name,
        "author": user.name if hasattr(user, 'name') and user.name else "사용자",
        "views": "0",
        "rank": rank,
        "imageUrl": request.imageUrl,
        "type": request.type,
        "gender": request.gender,
        "age": request.age,
        "details": request.details,
        "prompt": request.prompt
    }
    characters.append(new_char)
    save_characters(characters)
    return new_char
