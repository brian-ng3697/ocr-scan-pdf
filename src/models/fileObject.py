from datetime import datetime, timezone
from typing import List
from pydantic import BaseModel
import typing

class FileObject(BaseModel):
    id: str
    file_path: str
    name: str
    size: int
    mime_type: str
    provider: str
    uploader: str # userId
    image_content: typing.Optional[typing.Any] # OPTIONAL, could be String or Object
    text_locale: typing.Optional[str] # OPTIONAL
    download_link: typing.Optional[str]# OPTIONAL
    
    tags: List[str] = []
    metadata: dict = {}
    created_at: datetime = datetime.now(tz=timezone.utc)
    updated_at: datetime = None
    deleted_at: datetime = None
