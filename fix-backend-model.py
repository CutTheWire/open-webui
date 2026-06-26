import re

file_path = "backend/open_webui/routers/character_chat.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Update Models
content = re.sub(
    r"class Character\(BaseModel\):\n.*?class CharacterCreateRequest\(BaseModel\):\n.*?\n\n",
    """class Character(BaseModel):
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
    prompt: str = ""\n\n""",
    content,
    flags=re.DOTALL
)

# Remove default characters
content = re.sub(
    r"def load_characters\(\) -> List\[dict\]:\n    if not CHARACTERS_JSON_PATH.exists\(\):\n.*?(?=\n    try:\n        with open\(CHARACTERS_JSON_PATH)",
    """def load_characters() -> List[dict]:
    if not CHARACTERS_JSON_PATH.exists():
        save_characters([])
        return []""",
    content,
    flags=re.DOTALL
)

# Update create_character
content = re.sub(
    r"        \"imageUrl\": request\.imageUrl,\n        \"gender\": request\.gender,\n        \"age\": request\.age,\n        \"details\": request\.details\n    }",
    """        "imageUrl": request.imageUrl,
        "type": request.type,
        "gender": request.gender,
        "age": request.age,
        "details": request.details,
        "prompt": request.prompt
    }""",
    content
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
