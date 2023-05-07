import asyncio
from turtle import width
from typing import Any
from matplotlib.pyplot import text
import uvicorn
import requests
from urllib.parse import urlparse
import json

# fastapi
from fastapi import FastAPI, File, UploadFile, Header, Request, status, Depends, Query, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

# fastapi_limiter
from fastapi_limiter import FastAPILimiter
from src.db.dbSingleton import DBSingleton

# conversion 
from src.routes import router as endpointRouter

# Response model
from src.models.response import Response

from src.services.fileManagement import FileManagement
from src.services.userManagement import UserManagement


fMgm = FileManagement()
uMgm = UserManagement()

tags_metadata = [
  {
      "name": "PDF",
      "description": "PDF Manipulation",
  }
]

# app = FastAPI(dependencies=[Depends(JWTBearer())])
description = """
OCR document scan APIs 🚀
"""
app = FastAPI(
  docs_url='/documentation',
  redoc_url=None,
  title="OCR APIs",
  description="OCR document scan APIs 🚀",
  version="1.0.6",
  terms_of_service="http://example.com/terms/",
  contact={
      "name": "Johnathan",
      "url": "http://example.com",
      "email": "transybao28@gmail.com",
  },
  license_info={
      "name": "Apache 2.0",
      "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
  },
  openapi_tags=tags_metadata
)

# CORS
origins = [
  'http://localhost:8000',
  'http://localhost:3000',
  'http://localhost:5000',
  'http://localhost:9000',
  'https://sota-free.vercel.app',
  'https://main.d8udn8pt8zdr2.amplifyapp.com',
  'https://dev.viescan.tech',
  'https://viescan.tech'
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
  try:
    redis = DBSingleton.get_instance()
    await FastAPILimiter.init(redis)
  except Exception as e:
    print("on_event Startup error: ", e)

app.include_router(endpointRouter)

# static files
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
  log_config = uvicorn.config.LOGGING_CONFIG
  log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
  uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_config=log_config)