from minio import Minio
from ..config.config import settings

cloudFS = Minio(
  settings.FileStorageSettings.Endpoint,
  access_key=settings.FileStorageSettings.AccessKey,
  secret_key=settings.FileStorageSettings.SecretKey,
)