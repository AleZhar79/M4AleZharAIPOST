from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ---------- Source ----------
class SourceBase(BaseModel):
    type: str          # "site" или "tg"
    name: str
    url: str
    enabled: bool = True


class SourceCreate(SourceBase):
    pass


class SourceUpdate(BaseModel):
    type: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None
    enabled: Optional[bool] = None


class SourceOut(SourceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ---------- Keyword ----------
class KeywordBase(BaseModel):
    word: str


class KeywordCreate(KeywordBase):
    pass


class KeywordUpdate(BaseModel):
    word: Optional[str] = None


class KeywordOut(KeywordBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ---------- Post ----------
class PostBase(BaseModel):
    generated_text: str
    news_id: Optional[int] = None
    status: str = "new"


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    generated_text: Optional[str] = None
    status: Optional[str] = None
    published_at: Optional[datetime] = None


class PostOut(PostBase):
    id: int
    published_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
