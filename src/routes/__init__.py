from fastapi import APIRouter, Depends
from .pdf import pdfRouter

router = APIRouter()
router.include_router(pdfRouter, prefix="/pdf", tags=['PDF'])