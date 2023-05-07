from copy import copy
import magic
import io
import os
import hashlib
from datetime import datetime, timedelta

from google.cloud.firestore_v1 import DocumentSnapshot, DocumentReference
from google.cloud import firestore
from fastapi import UploadFile
from cachetools import TTLCache


from ..models.errorModel import ErrorInfoContainer
from ..models.userModel import UserModel, UserStatsModel
from ..db.dbSingleton import FirestoreDBSingleton
from ..db.fireStoreDB import ListCollection
from ..dependencies.cloudStorage import cloudFS
from ..config.config import settings


dbi = FirestoreDBSingleton().get_instance()
uMGMCache = TTLCache(
    maxsize=1000,
    ttl=timedelta(minutes=5),
    timer=datetime.now
)

MAXIMUM_AVATAR_UPLOAD_SIZE = 5 * 1048576
ALLOWED_AVATAR_MIME_TYPES = [
    'image/png',
    'image/jpeg',
]


class UserManagement:
    def __init__(self) -> None:
        self.__collection = dbi.collection(ListCollection.BASE.value)
        self.__statsColl = dbi.collection(ListCollection.STATS.value)

    # FIXME: Need to rename this function, could be "GetSingleProfile"
    def Info(self, email: str, fromCache=True):
        cKey = self.__getCacheKey("info", email)
        if fromCache and uMGMCache.get(cKey) is not None:
            return uMGMCache.get(cKey)

        docPath = self.__getPathRef(email)
        docRef = self.__collection.document(docPath).get()
        if self.__isDocExists(docRef) is False:
            raise ErrorInfoContainer.not_found_error

        res = self.__parseFromDoc(docRef)
        uMGMCache[cKey] = res
        return res

    def IsExist(self, email: str):
        docRef = self.__collection.document(self.__getPathRef(email)).get()
        return self.__isDocExists(docRef)

    def Save(self, userInfo: UserModel, file: UploadFile = None):
        docRef = self.__collection.document(self.__getPathRef(userInfo.email))

        if file is not None:
            userInfo.picture = self.__uploadAvatar(userInfo.email, file)

        # Update db and clear cache
        docRef.set(document_data=userInfo.dict(), merge=True)
        if uMGMCache.get(self.__getCacheKey("info", userInfo.email)) is not None:
            uMGMCache.__delitem__(self.__getCacheKey("info", userInfo.email))

    # Update user stats
    def UpdateStats(self, email: str, stats: UserStatsModel, timeStats: datetime = datetime.utcnow()):
        docRef = self.__statsColl.document(self.__getStatsPathRef(email))
        cKey = self.__getCacheKey("stats", email)

        self.__updateStatsAndClearCache(docRef=docRef, stats=stats, cacheKey=cKey)

        # Update current monthly stats only
        if timeStats is not None:
            self.UpdateMonthlyStats(email, stats, timeStats)

    # Update user stats
    def UpdateMonthlyStats(self, email: str, stats: UserStatsModel, timeStats: datetime = datetime.utcnow()):
        statsName = self.__getMonthStatsDocName(timeStats)
        cKey = self.__getCacheKey("monthly_stats:{}".format(statsName), email)
        docRef = self.__statsColl.document(
            self.__getStatsPathRef(email, monthStats=statsName))
            
        self.__updateStatsAndClearCache(docRef=docRef, stats=stats, cacheKey=cKey)


    # Get user stats
    def Stats(self, email: str):
        cKey = self.__getCacheKey("stats", email)
        if uMGMCache.get(cKey) is not None:
            return uMGMCache.get(cKey)

        docRef = self.__statsColl.document(self.__getStatsPathRef(email))
        stats = docRef.get()
        if stats.exists == False:
            return UserStatsModel()

        res = UserStatsModel.parse_obj(stats.to_dict())
        uMGMCache[cKey] = res

        return res

    # Get Monthly Stats
    def MonthlyStats(self, email: str, timeStats: datetime = datetime.utcnow()):
        statsName = self.__getMonthStatsDocName(timeStats)
        cKey = self.__getCacheKey("monthly_stats:{}".format(statsName), email)
        if uMGMCache.get(cKey) is not None:
            return uMGMCache.get(cKey)

        docRef = self.__statsColl.document(
            self.__getStatsPathRef(email, statsName))

        stats = docRef.get()
        if stats.exists == False:
            return UserStatsModel()

        res = UserStatsModel.parse_obj(stats.to_dict())
        uMGMCache[cKey] = res

        return res

    def __updateStatsAndClearCache(self, docRef: DocumentReference, stats: UserStatsModel, cacheKey: str):
         # Init stats
        if docRef.get().exists is False:
            docRef.set(stats.dict(), merge=True)
            return

        updateVals = {}
        data = stats.dict()
        for k in data:
            if data[k] == 0:
                continue
            updateVals[k] = firestore.Increment(data[k])

        # Update db and clear cache
        docRef.update(updateVals)
        if uMGMCache.get(cacheKey) is not None:
            uMGMCache.__delitem__(cacheKey)


    def __uploadAvatar(self, email: str, file: UploadFile):
        docRef = self.__collection.document(self.__getPathRef(email))
        if docRef.get().exists == False:
            raise ErrorInfoContainer.not_found_error

        fileContent = file.file.read()

        # No need all data for mime type detection
        mimeType = magic.from_buffer(fileContent[:1024],  mime=True)

        # Limit maximum file size
        if len(fileContent) > MAXIMUM_AVATAR_UPLOAD_SIZE:
            raise ErrorInfoContainer.file_too_large

        # Limit file type to upload
        if mimeType not in ALLOWED_AVATAR_MIME_TYPES:
            raise ErrorInfoContainer.file_type_is_not_allowed

        bucket = settings.FileStorageSettings.Bucket
        filePath = self.__getCloudPath(email, file.filename)

        cloudFS.put_object(
            bucket,
            data=io.BytesIO(fileContent),
            object_name=filePath,
            length=-1,
            content_type=mimeType,
            part_size=10*1024*1024
        )
        return filePath

    def __getPathRef(self, email: str) -> str:
        return "%s" % (email)

    def __parseFromDoc(self, doc: DocumentSnapshot) -> UserModel:
        return UserModel.parse_obj(doc.to_dict())

    def GetAvatarLink(self, user: UserModel) -> UserModel:
        bucket = settings.FileStorageSettings.Bucket
        usr = copy(user)
        if len(usr.picture) > 0 and usr.picture.startswith("http") == False:
            usr.picture = cloudFS.get_presigned_url("GET", bucket, usr.picture)

        return usr

    def __getStatsPathRef(self, email: str, monthStats: str = "") -> str:
        if monthStats != "":
            return "{}/months/{}".format(email, monthStats)
        return "{}".format(email)

    def __getMonthStatsDocName(self, currTime: datetime = datetime.utcnow()) -> str:
        return currTime.strftime("%Y_%m")

    def __isDocExists(self, doc: DocumentSnapshot) -> bool:
        return doc.exists and ('email' in doc.to_dict())

    def __getCloudPath(self, userId: str, fileName: str):
        cloudPath = "avatars/%s" % (hashlib.md5(userId.encode()).hexdigest())

        # Append file extension
        ext = os.path.splitext(fileName.lower())
        if len(ext) > 1:
            cloudPath += ext[1]

        return cloudPath

    def __getCacheKey(self, prefix: str, userId: str) -> str:
        return "%s:%s" % (prefix, userId)
