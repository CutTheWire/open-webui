from __future__ import annotations

import logging
import time
from typing import Optional, List
from uuid import uuid4

from open_webui.internal.db import Base, get_async_db_context
from pydantic import BaseModel, ConfigDict
from sqlalchemy import (
    BigInteger,
    Column,
    Text,
    select,
    Index,
    func,
    Integer,
)
from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger(__name__)

####################
# Character DB Schema
####################

class Character(Base):
    __tablename__ = 'character_chat'

    id = Column(Text, primary_key=True, unique=True)
    type = Column(Text, nullable=False)  # "character" or "story"
    name = Column(Text, nullable=False)
    author = Column(Text, nullable=False)
    views = Column(Text, default="0")
    rank = Column(Integer, nullable=False)
    imageUrl = Column(Text, nullable=False)
    
    # Character specific
    gender = Column(Text, default="")
    age = Column(Text, default="")
    details = Column(Text, default="")
    
    # Story specific
    prompt = Column(Text, default="")

    created_at = Column(BigInteger, nullable=False)
    updated_at = Column(BigInteger, nullable=False)


class CharacterModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: str
    name: str
    author: str
    views: str
    rank: int
    imageUrl: str
    gender: str = ""
    age: str = ""
    details: str = ""
    prompt: str = ""
    created_at: int
    updated_at: int


class CharacterCreateRequest(BaseModel):
    type: str = "character"
    name: str
    imageUrl: str
    gender: str = ""
    age: str = ""
    details: str = ""
    prompt: str = ""


class CharactersTable:
    async def get_all_characters(self, db: Optional[AsyncSession] = None) -> List[CharacterModel]:
        async with get_async_db_context(db) as session:
            stmt = select(Character).order_by(Character.rank.asc())
            result = await session.execute(stmt)
            characters = result.scalars().all()
            return [CharacterModel.model_validate(c) for c in characters]

    async def get_character_by_id(self, id: str, db: Optional[AsyncSession] = None) -> Optional[CharacterModel]:
        async with get_async_db_context(db) as session:
            stmt = select(Character).where(Character.id == id)
            result = await session.execute(stmt)
            character = result.scalar_one_or_none()
            if character:
                return CharacterModel.model_validate(character)
            return None

    async def insert_new_character(
        self, author: str, form_data: CharacterCreateRequest, db: Optional[AsyncSession] = None
    ) -> Optional[CharacterModel]:
        async with get_async_db_context(db) as session:
            # Calculate rank
            count_stmt = select(func.count(Character.id))
            count_result = await session.execute(count_stmt)
            count = count_result.scalar_one()
            rank = count + 1

            new_character = Character(
                id=str(uuid4()),
                type=form_data.type,
                name=form_data.name,
                author=author,
                views="0",
                rank=rank,
                imageUrl=form_data.imageUrl,
                gender=form_data.gender,
                age=form_data.age,
                details=form_data.details,
                prompt=form_data.prompt,
                created_at=int(time.time()),
                updated_at=int(time.time()),
            )
            session.add(new_character)
            await session.commit()
            return CharacterModel.model_validate(new_character)


Characters = CharactersTable()
