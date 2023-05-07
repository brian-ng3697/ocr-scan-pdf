from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth, credentials
import json
from ..config.config import settings
from ..models.errorModel import ErrorInfoModel
from ..dependencies.docsconv.exceptions import BaseError
from fastapi import status

from ..services.userManagement import UserManagement
from ..services.folderManagement import FolderManagement
from ..models.userModel import UserModel
from ..models.folderModel import FolderModel
from ..models.planFeature import FREE_PLAN_FEATURE
from ..models.platformFeature import APP_PLATFORM_FEATURE, WEB_PLATFORM_FEATURE

# firebase_admin, service account file
jsonCred = json.loads(settings.AuthSettings.FireBaseCredentials)
cred = credentials.Certificate(jsonCred)
firebase_admin.initialize_app(cred)

uMgm = UserManagement()
fMgm = FolderManagement()

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        userDict: dict = {}
        try:
            credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
            if credentials:
                if not credentials.scheme == "Bearer":
                    raise HTTPException(
                        status_code=403, detail="Invalid authentication scheme.")

                userDict = self.JWTVerify(credentials.credentials)
                if len(userDict) == 0:
                    raise HTTPException(
                        status_code=403, detail="Invalid token or expired token.")

                # Set userDict to request state
                request.state.userDict = userDict

                # Set platform to request
                platform = APP_PLATFORM_FEATURE.name
                if request._headers.get("Platform") != None and str(request._headers.get("Platform")).lower() == WEB_PLATFORM_FEATURE.name:
                    platform = WEB_PLATFORM_FEATURE.name

                request.state.platform = platform
                
                # Check user info and update in cloud
                if uMgm.IsExist(userDict[u'email']) is False:
                    info = UserModel(
                            name=userDict[u'name'],
                            user_id=userDict[u'user_id'],
                            picture=userDict[u'picture'],
                            email=userDict[u'email'], 
                            current_plan= FREE_PLAN_FEATURE.name
                        )
                    uMgm.Save(userInfo=info)
                
                if fMgm.IsExist(userDict[u'email'], settings.FolderSettings.RootFolder) is False:
                    fMgm.Save(email=userDict[u'email'], fObj=FolderModel(
                        id=settings.FolderSettings.RootFolder,
                        name=settings.FolderSettings.RootFolder
                    ))
        except HTTPException as e:
            raise e
        except BaseError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=e.getMessage())
        except ErrorInfoModel as e:
            raise HTTPException(
                status_code=e.http_status, detail=e.message)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error %s" % (e))
        return userDict


    def JWTVerify(self, idToken: str) -> dict:
        userDict: dict = {}
        try:
            payload = auth.verify_id_token(id_token=idToken)
            if payload:
                userDict = payload
        except HTTPException as e:
            raise e
        except BaseError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=e.getMessage())
        except ErrorInfoModel as e:
            raise HTTPException(
                status_code=e.http_status, detail=e.message)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error %s" % (e))
        return userDict