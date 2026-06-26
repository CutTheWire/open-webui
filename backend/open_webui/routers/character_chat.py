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
    name: str
    author: str
    views: str
    rank: int
    imageUrl: str
    gender: str
    age: str
    details: str

class CharacterCreateRequest(BaseModel):
    name: str
    imageUrl: str
    gender: str
    age: str
    details: str


def load_characters() -> List[dict]:
    if not CHARACTERS_JSON_PATH.exists():
        # 기본 캐릭터 데이터
        default_characters = [
            {
                "id": "1",
                "name": "들어오면 만지게 해줄게",
                "author": "맛도리네",
                "views": "350.3K",
                "rank": 1,
                "imageUrl": "https://d394jeh9729epj.cloudfront.net/8uzw2bB3duM-GGKOOUpKVVo5/e790d9e0-d7ce-40d5-8b30-831078b97b1d_q70_gif600.webp",
                "gender": "여성",
                "age": "20대",
                "details": "사용자를 유혹하는 성격. 거침없는 말투."
            },
            {
                "id": "2",
                "name": "아카데미는 힘이 곧 매력",
                "author": "뮤지개",
                "views": "237.3K",
                "rank": 2,
                "imageUrl": "https://d394jeh9729epj.cloudfront.net/8PT1uF8SRPy-GGKOTTVDQkdC/ee85cb99-c271-4d7d-87a8-1028c2041913_q70_gif600.webp",
                "gender": "여성",
                "age": "10대",
                "details": "아카데미의 힘을 숭배하는 캐릭터. 무뚝뚝하지만 다정한 말투."
            },
            {
                "id": "3",
                "name": "언제나 웃는 마을버스 R",
                "author": "대파조아",
                "views": "86.8K",
                "rank": 3,
                "imageUrl": "https://d394jeh9729epj.cloudfront.net/8FnqcPT9U1q-GGKOWTBKWkgz/b7d7d118-cf88-44bf-bed0-2b40bb26bde9_w600.webp",
                "gender": "여성",
                "age": "20대",
                "details": "언제나 친절하게 웃는 캐릭터. 상냥한 말투."
            },
            {
                "id": "4",
                "name": "혼수상태 여동생",
                "author": "땁따비땁",
                "views": "88.9K",
                "rank": 4,
                "imageUrl": "https://d394jeh9729epj.cloudfront.net/8EissCzWvEQ-GGKOSVZXMzAw/3e466d8f-d21e-4fec-9583-e99995d5ee68_q70_gif600.webp",
                "gender": "여성",
                "age": "10대",
                "details": "여동생 캐릭터. 소심하지만 오빠를 의지하는 성격."
            },
            {
                "id": "5",
                "name": "육상부 여신 타락일지",
                "author": "서단유",
                "views": "144.5K",
                "rank": 5,
                "imageUrl": "https://d394jeh9729epj.cloudfront.net/8LJ9OImrLKo-GGKONDM1OUpP/333fe924-bf7a-4b0b-b827-39cee5dbe275_q70_gif600.webp",
                "gender": "여성",
                "age": "10대",
                "details": "육상부 에이스. 자신만만하고 활기찬 성격."
            },
            {
                "id": "6",
                "name": "！우당탕탕！ 콘코르디아 아카데미 U",
                "author": "코기토",
                "views": "131.8K",
                "rank": 6,
                "imageUrl": "https://d394jeh9729epj.cloudfront.net/8E7K2CU2heE-KKKOQ000M1I2/43fdc472-0402-4de6-8a9a-61220b9cd6a0_q70_gif600.webp",
                "gender": "여성",
                "age": "10대",
                "details": "활발하고 시끄러운 성격. 장난기 많은 말투."
            }
        ]
        save_characters(default_characters)
        return default_characters
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
        "gender": request.gender,
        "age": request.age,
        "details": request.details
    }
    characters.append(new_char)
    save_characters(characters)
    return new_char
