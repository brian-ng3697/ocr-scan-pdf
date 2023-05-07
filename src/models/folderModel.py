from pydantic import BaseModel
from datetime import datetime, timezone
from typing import List

class FolderModel(BaseModel):
    id: str = ""
    name: str
    files: List[str] = []
    created_at: datetime = datetime.now(tz=timezone.utc)
    updated_at: datetime = None
    deleted_at: datetime = None

class GetFolderDTO(BaseModel):
    id: str
    name: str
    files: List[str] = []
    countFile: int
    created_at: datetime = datetime.now(tz=timezone.utc)
    updated_at: datetime = None

class CreateAndUpdateFolderDTO(BaseModel):
    name: str

class TransferFolderDTO(BaseModel):
    fromFolderId: str = ""
    toFolderId: str = ""
    files: List[str]