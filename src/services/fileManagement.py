
import os
import io
import magic
import uuid
from typing import List, Any
from datetime import datetime, timezone
from fastapi import HTTPException, status

from fastapi import UploadFile
from pydantic import BaseModel
from google.cloud.firestore_v1 import DocumentSnapshot

from .userManagement import UserManagement
from .featureLimit import FeatureLimit
from ..config.config import settings
from ..db.dbSingleton import FirestoreDBSingleton
from ..db.fireStoreDB import ListCollection
from ..models.errorModel import ErrorInfoContainer
from ..models.fileObject import FileObject
from ..models.userModel import UserStatsModel, UserModel
from ..dependencies.cloudStorage import cloudFS
from google.cloud import firestore

dbi = FirestoreDBSingleton.get_instance()
uMGM = UserManagement()

DEFAULT_LIMIT_PER_PAGE = 50
ALLOWED_MIME_TYPES = [
    'image/*',
    'image/png',
    'image/jpeg',
    'image/bmp',
    'image/tiff',
    'image/webp',
    # 'image/x-portable-bitmap', # this image type is not stable for preprocessing and detection
    'image/x-portable-graymap',
    'image/x-portable-pixmap',
    'image/x-portable-anymap',

    'application/rtf',
    'application/pdf',

    # MS Office
    'application/msword',
    'application/vnd.ms-powerpoint',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',


    # Open Office
    'application/vnd.oasis.opendocument.presentation',
    'application/vnd.oasis.opendocument.spreadsheet',
    'application/vnd.oasis.opendocument.text'
]


class FileFilters(BaseModel):
    limit: int = DEFAULT_LIMIT_PER_PAGE
    mimeTypes: List[str] = []
    files: List[str] = []
    deletedOnly: bool = False


class FileManagement:
    # constructor
    def __init__(self):
        self.__collection = dbi.collection(ListCollection.BASE.value)

    def Get(self, userId: str, fileId: str) -> FileObject:
        """Get file info of user

        Args:
            userId (str): _description_
            fileId (str): _description_

        Raises:
            ErrorInfoContainer.not_found_error: _description_

        Returns:
            FileObject: _description_
        """
        docRef = self.__collection.document(self.__getRef(userId, fileId))
        doc = docRef.get()
        if doc.exists == False:
            raise ErrorInfoContainer.not_found_error

        return self.parseFileObjectFromDoc(doc)

    def CreateFromPathAndDownloadLink(self, userId: str, filePath: str, tags: List[str] = [], metadata: dict = {}) -> str:
        """CreateFromPathAndDownloadLink

        Args:
            userId (str): _description_
            filePath (str): _description_
            tags (List[str], optional): _description_. Defaults to [].
            metadata (dict, optional): _description_. Defaults to {}.

        Returns:
            str: _description_
        """
        fileLocal = open(filePath, 'rb')
        fData = fileLocal.read()
        fileName = "{0} {1}".format(os.path.basename(filePath).split('.')[0], datetime.now())
        fObj = self.CreateFromContent(
            userId=userId, fileName=fileName, fileContent=fData, tags=tags, metadata=metadata)
        if len(fObj.file_path) == 0:
            return ""
        return cloudFS.get_presigned_url('GET', bucket_name=settings.FileStorageSettings.Bucket, object_name=fObj.file_path)

    def CreateFromFileUpload(self, userId: str, file: UploadFile, tags: List[str] = [], metadata: dict = {}) -> FileObject:
        """CreateFromFileUpload

        Args:
            userId (str): _description_
            file (UploadFile): _description_
            tags (List[str], optional): _description_. Defaults to [].
            metadata (dict, optional): _description_. Defaults to {}.

        Raises:
            ErrorInfoContainer.file_type_is_not_allowed: _description_

        Returns:
            FileObject: _description_
        """
        fData = file.file.read()

        # No need all data for mime type detection
        mimeType = magic.from_buffer(fData[:1024],  mime=True)

        # Limit file type to upload
        if mimeType not in ALLOWED_MIME_TYPES:
            raise ErrorInfoContainer.file_type_is_not_allowed
            
        fName = "{0} {1}".format(file.filename.split('.')[0], datetime.now())

        return self.CreateFromContent(userId=userId, fileName=fName, fileContent=fData, tags=tags, metadata=metadata)

    def CreateFromContent(self, userId: str, fileName: str, fileContent, tags: List[str] = [], metadata: dict = {}) -> FileObject:
        """Create and upload file to remote storage

        Args:
            userId (str): _description_
            fileName (str): _description_
            fileContent (binary): _description_
            tags (List[str], optional): _description_. Defaults to [].
            metadata (dict, optional): _description_. Defaults to {}.

        Returns:
            FileObject: _description_
        """

         # File upload size double check
        FeatureLimit.IsValidOrRaiseCustomException(userId, "file_capacity", len(fileContent), ErrorInfoContainer.file_too_large)

        cloudPath, newId = self.__getCloudPath(userId, fileName)
        bucket = settings.FileStorageSettings.Bucket
        mimeType = magic.from_buffer(fileContent[:1024],  mime=True)
        if metadata.get("mimeType") is not None:
            mimeType = metadata.get("mimeType")

        cloudFS.put_object(
            bucket,
            data=io.BytesIO(fileContent),
            object_name=cloudPath,
            length=-1,
            content_type=mimeType,
            part_size=10*1024*1024
        )

        res = self.Create(userId, FileObject(
            id=newId,
            file_path=cloudPath,
            uploader=userId,
            name=fileName,
            size=len(fileContent),
            mime_type=mimeType,
            provider=settings.FileStorageSettings.Endpoint,
            tags=tags,
            metadata=metadata
        ))

        # Update user stats
        uMGM.UpdateStats(userId, UserStatsModel(
            cloud_space_total_file=1,
            cloud_space_total_size=len(fileContent)
        ))

        return res

    def Create(self, userId: str, fObj: FileObject) -> FileObject:
        """Just create file object and save to DB

        Args:
            userId (str): _description_
            fObj (FileObject): _description_

        Returns:
            FileObject: _description_
        """
        # Store data to DB
        if len(fObj.id) == 0:
            fObj.id = str(uuid.uuid4())

        fObj.created_at = datetime.now(tz=timezone.utc)
        fdoc = self.__collection.document(self.__getRef(userId, fObj.id))
        fdoc.set(fObj.dict())
        return self.parseFileObjectFromDoc(fdoc.get())

    def Update(self, userId: str, fObj: FileObject) -> FileObject:
        """Update file info and metadata

        Args:
            userId (str): _description_
            fObj (FileObject): _description_

        Raises:
            ErrorInfoContainer.not_found_error: _description_

        Returns:
            FileObject: _description_
        """
        # Update file info
        docRef = self.__collection.document(self.__getRef(userId, fObj.id))
        if docRef.get().exists == False:
            raise ErrorInfoContainer.not_found_error

        fObj.updated_at = datetime.now(tz=timezone.utc)
        docRef.set(fObj.dict())

        return self.parseFileObjectFromDoc(docRef.get())

    def SoftDelete(self, userId: str, fileId: str):
        """Just update set time deletedAt. Not really delete file on storage

        Args:
            userId (str): _description_
            fileId (str): _description_

        Raises:
            ErrorInfoContainer.not_found_error: _description_
        """
        docRef = self.__collection.document(self.__getRef(userId, fileId))
        doc = docRef.get()
        if docRef.get().exists == False:
            raise ErrorInfoContainer.not_found_error

        fObj = self.parseFileObjectFromDoc(doc)
        fObj.deleted_at = datetime.now(tz=timezone.utc)
        docRef.set(fObj.dict())

        # Update user stats
        uMGM.UpdateStats(userId, UserStatsModel(
            cloud_space_total_file=-1,
            cloud_space_total_size=(fObj.size * -1)
        ), timeStats=fObj.created_at)

    def GetListFile(self, userId: str, options: FileFilters) -> List[FileObject]:
        """Get list file of user

        Args:
            userId (str): _description_
            options (FileFilters): _description_

        Returns:
            List[FileObject]: _description_
        """
        filesColl = self.__collection.document(userId).collection('files')

        if options.deletedOnly:
            filesColl = filesColl.where(u'deleted_at', u'>', datetime.min)
        else:
            filesColl = filesColl.where(u'deleted_at', u'==', None)

        if len(options.files) > 0:
            filesColl = filesColl.where(
                u'id', u'in', options.files)

        if len(options.mimeTypes) > 0:
            filesColl = filesColl.where(u'mime_type', u'in', options.mimeTypes)
        filesColl.order_by(u'created_at')
        docs = filesColl.stream()

        res = []
        for doc in docs:
            res.append(self.parseFileObjectFromDoc(doc))

        return res
    
    def GetDownloadLink(self, fObj: FileObject) -> str:
        """Get remote storage download link

        Args:
            fObj (FileObject): _description_

        Returns:
            str: _description_
        """
        if len(fObj.file_path) == 0:
            return ""
        return cloudFS.get_presigned_url('GET', bucket_name=settings.FileStorageSettings.Bucket, object_name=fObj.file_path)

    def __getCloudPath(self, userId: str, fileName: str):
        newId = str(uuid.uuid4())
        cloudPath = 'files/%s/%s' % (userId, newId)

        # Append file extension
        ext = os.path.splitext(fileName.lower())
        if len(ext) > 1:
            cloudPath += ext[1]

        return cloudPath, newId

    def CreateFromPath(self, userId: str, filePath: str, tags: List[str] = [], metadata: dict = {}) -> FileObject:
        """Create file by filepath and upload to remote storage

        Args:
            userId (str): _description_
            filePath (str): _description_
            tags (List[str], optional): _description_. Defaults to [].
            metadata (dict, optional): _description_. Defaults to {}.

        Returns:
            FileObject: _description_
        """
        print('on CreateFromPath function with ' + userId)
        fileLocal = open(filePath, 'rb')
        fData = fileLocal.read()
        fileName = "{0} {1}".format(os.path.basename(filePath).split('.')[0], datetime.now())
        fObj = self.CreateFromContent(
            userId=userId, fileName=fileName, fileContent=fData, tags=tags, metadata=metadata)
        if len(fObj.file_path) == 0:
            return None
        return fObj

     # save file data without file itself, it is image content
    def UpdateFileImageContentAndLocale(self, imageContent, locale: str, fObj: FileObject):
        """Save file data without file itself, it is image content

        Args:
            imageContent (str): _description_
            fObj (FileObject): _description_

        Raises:
            ErrorInfoContainer.not_found_error: _description_

        Returns:
            FileObject: _description_
        """
        # Update file info
        docRef = self.__collection.document(
            self.__getRef(fObj.uploader, fObj.id))
        if docRef.get().exists == False:
            raise ErrorInfoContainer.not_found_error

        # Update file image content, content locale
        fObj.image_content = imageContent
        fObj.text_locale = locale
        fObj.updated_at = datetime.now(tz=timezone.utc)
        docRef.set(fObj.dict())

        # Update statistic number
        self.UpdateTotalOCRCount(fObj.uploader)
        return self.parseFileObjectFromDoc(docRef.get())

    # DB path reference
    def __getRef(self, userId: str, fileId: str) -> str:
        return '%s/files/%s' % (userId, fileId)

    def parseFileObjectFromDoc(self, doc: DocumentSnapshot) -> FileObject:
        return FileObject.parse_obj(doc.to_dict())

    # FIXME: We can fix this function to actually update any UserStat property as we want, 
    # the input will be UserStatsModel with data 
    def UpdateTotalOCRCount(self, userEmail: str):
        try:
            userStatModelData = UserStatsModel(
                cloud_ocr_per_month=1
            )
            uMGM.UpdateMonthlyStats(userEmail, userStatModelData, timeStats=datetime.now(tz=timezone.utc))
        except Exception as e:
            raise Exception("UpdateTotalOCRCount failed with error: {0}".format(e))

    def UpdateImageToDocxCount(self, userEmail: str):
        # FIXME: We can fix this function to actually update any UserStat property as we want, 
        # the input will be UserStatsModel with data 
        try:
            userStatModelData = UserStatsModel(
                image_to_docx_per_month=1,
                cloud_ocr_per_month=1,
            )
            uMGM.UpdateStats(userEmail, userStatModelData, timeStats=datetime.now(tz=timezone.utc))
        except Exception as e:
            raise Exception("UpdateImageToDocxCount failed with error: {0}".format(e))
    
    def UpdateImageToPdfCount(self, userEmail: str):
        try:
            userStatModelData = UserStatsModel(
                image_to_pdf_per_month=1,
                cloud_ocr_per_month=1,
            )
            uMGM.UpdateStats(userEmail, userStatModelData, timeStats=datetime.now(tz=timezone.utc))
        except Exception as e:
            raise Exception("UpdateImageToPdfCount failed with error: {0}".format(e))

    def UpdateTextToDocxCount(self, userEmail: str):
        try:
            userStatModelData = UserStatsModel(
                text_to_docx_per_month=1
            )
            uMGM.UpdateStats(userEmail, userStatModelData, timeStats=datetime.now(tz=timezone.utc))
        except Exception as e:
            raise Exception("UpdateTextToDocxCount failed with error: {0}".format(e))
    
    def UpdateTextToPdfCount(self, userEmail: str):
        try:
            userStatModelData = UserStatsModel(
                text_to_pdf_per_month=1
            )
            uMGM.UpdateStats(userEmail, userStatModelData, timeStats=datetime.now(tz=timezone.utc))
        except Exception as e:
            raise Exception("UpdateTextToPdfCount failed with error: {0}".format(e))

    def UpdateFileConvertionCount(self, userEmail: str):
        try:
            userStatModelData = UserStatsModel(
                file_conversion_per_month=1
            )
            uMGM.UpdateStats(userEmail, userStatModelData, timeStats=datetime.now(tz=timezone.utc))
        except Exception as e:
            raise Exception("UpdateFileConvertionCount failed with error: {0}".format(e))
    
    def UpdatePdfManipulationCount(self, userEmail: str):
        try:
            userStatModelData = UserStatsModel(
                pdf_manipulation_per_month=1
            )
            uMGM.UpdateStats(userEmail, userStatModelData, timeStats=datetime.now(tz=timezone.utc))
        except Exception as e:
            raise Exception("UpdatePdfManipulationCount failed with error: {0}".format(e))