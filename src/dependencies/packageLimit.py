
from fastapi import Request, Header
from ..services.featureLimit import FeatureLimit
from ..services.userManagement import UserManagement
import json

uMgm = UserManagement()

class PackageLimit:

    def __init__(self) -> None:
        pass

    # FIXME: Can be separate into general and specific feature package limit
    # General feature package limit
    async def FileLimitDependency(self, request: Request, content_length: int = Header(include_in_schema=False)):        
        usrEmail = request.state.userDict[u'email']
        currentFileCount = uMgm.Stats(usrEmail).cloud_space_total_file
        FeatureLimit.IsValidOrRaiseHttpException(usrEmail, "cloud_space_total_file", currentFileCount)
        FeatureLimit.IsValidOrRaiseHttpException(usrEmail, "file_capacity", content_length)

    
    async def PdfManipulationLimitDependency(self, request: Request):
        usrEmail = request.state.userDict[u'email']
        currentPdfManipulation = uMgm.MonthlyStats(usrEmail).pdf_manipulation_per_month
        FeatureLimit.IsValidOrRaiseHttpException(usrEmail, "pdf_manipulation_per_month", currentPdfManipulation)