from pydantic import BaseModel

# Base MimeType File 
class MimeTypeFeature(BaseModel):
    name: str

DOCX_MIME_TYPE = MimeTypeFeature(
    name="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)

DOC_MIME_TYPE = MimeTypeFeature(
    name="application/msword",
)
