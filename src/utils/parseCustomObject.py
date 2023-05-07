from ..models.errorModel import ErrorInfoContainer
from ..models.fileObject import FileObject
from ..models.userModel import UserStatsModel, UserModel
from google.cloud.firestore_v1 import DocumentSnapshot
from fastapi import HTTPException, status
from typing import Any

class ParseCustomObject():
    def __init__(self) -> None:
        pass

    def ParseCustomModelObject(self, modelName: str, doc: DocumentSnapshot) -> Any:
        if doc.exists == False:
            raise ErrorInfoContainer.not_found_error
        
        # FIXME: Need to create enum for this
        if modelName == 'fileModel':
            return FileObject.parse_obj(doc.to_dict())
        elif modelName == 'userStatModel':
            return UserStatsModel.parse_obj(doc.to_dict())
        elif modelName == 'userModel':
            return UserModel.parse_obj(doc.to_dict())
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{0} not gound".format(modelName)) 