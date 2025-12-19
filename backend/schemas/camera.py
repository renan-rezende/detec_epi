from pydantic import BaseModel
from typing import Optional


class CameraCreate(BaseModel):
    name: str
    url: str
    fps: int = 5


class CameraResponse(BaseModel):
    id: str
    name: str
    url: str
    fps: int
    active: bool = True


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    fps: Optional[int] = None
    active: Optional[bool] = None

