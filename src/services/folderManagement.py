import uuid
import numpy as np
from pydantic import BaseModel
from google.cloud.firestore_v1 import DocumentSnapshot
from ..models.errorModel import ErrorInfoContainer
from ..models.folderModel import FolderModel
from ..models.userModel import UserStatsModel
from ..db.dbSingleton import FirestoreDBSingleton
from ..db.fireStoreDB import ListCollection
from typing import List
from datetime import datetime, timezone
from ..config.config import settings
from .userManagement import UserManagement

dbi = FirestoreDBSingleton().get_instance()
uMGM = UserManagement()

class FolderFilters(BaseModel):
    limit: int = 50
    deletedOnly: bool = False

class FolderManagement:
    def __init__(self) -> None:
        self.__collection = dbi.collection(ListCollection.BASE.value)

    def Get(self, email: str, folderId: str):
        docRef = self.__collection.document(self.__getRef(email, folderId))
        doc = docRef.get()
        if doc.exists == False:
            raise ErrorInfoContainer.not_found_error

        return self.__parseFromDoc(doc)
    
    def IsExist(self, email: str, folderId: str):
        docRef = self.__collection.document(self.__getRef(email, folderId)).get()
        return self.__isExists(docRef)
    
    def GetListFolder(self, email: str, options: FolderFilters) -> List[FolderModel]:
        foldersColl = self.__collection.document(email).collection('folders')

        if options.deletedOnly:
            foldersColl = foldersColl.where(u'deleted_at', u'>', datetime.min)
        else:
            foldersColl = foldersColl.where(u'deleted_at', u'==', None)
        docs = foldersColl.stream()

        res = []
        for doc in docs:
            res.append(self.__parseFromDoc(doc))

        return res

    def Save(self, email: str, fObj: FolderModel):
        if len(fObj.id) == 0:
            fObj.id = str(uuid.uuid4())

        fdoc = self.__collection.document(self.__getRef(email, fObj.id))
        fdoc.set(fObj.dict())
        return self.__parseFromDoc(fdoc.get())
    
    def Update(self, email: str, fObj: FolderModel) -> FolderModel:
        docRef = self.__collection.document(self.__getRef(email, fObj.id))
        if docRef.get().exists == False:
            raise ErrorInfoContainer.not_found_error

        fObj.updated_at = datetime.now(tz=timezone.utc)
        docRef.set(fObj.dict())

        return self.__parseFromDoc(docRef.get())
    
    def SoftDelete(self, email: str, folderId: str):
        docRef = self.__collection.document(self.__getRef(email, folderId))
        doc = docRef.get()
        if docRef.get().exists == False:
            raise ErrorInfoContainer.not_found_error

        fObj = self.__parseFromDoc(doc)
        fObj.deleted_at = datetime.now(tz=timezone.utc)
        docRef.set(fObj.dict())

        return True
    
    def __isExists(self, doc: DocumentSnapshot) -> bool:
        return doc.exists

    def __getRef(self, email: str, folderId: str) -> str:
        return '%s/folders/%s' % (email, folderId)

    def __parseFromDoc(self, doc: DocumentSnapshot) -> FolderModel:
        return FolderModel.parse_obj(doc.to_dict())
    
    def UpdateStatsFolderCount(self, userEmail: str):
        try:
            userStatModelData = UserStatsModel(
                cloud_space_total_folder=1
            )
            uMGM.UpdateStats(userEmail, userStatModelData)
        except Exception as e:
            raise Exception("UpdateImageToWordCount failed with error: {0}".format(e))
    
    def AddFileFolderRoot(self, userEmail: str, fObjID: str):
        try:
            f = self.Get(userEmail, settings.FolderSettings.RootFolder)
            f.files = np.append(np.array(f.files), fObjID).tolist()
            self.Update(email=userEmail, fObj=f)
        except Exception as e:
            raise Exception("AddFileFolderRoot failed with error: {0}".format(e))
