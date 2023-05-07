from typing import Any, List

from fastapi import HTTPException, status

from ..opa.client import OPA
from ..models.errorModel import ErrorInfoModel, ErrorInfoContainer
from .userManagement import UserManagement

opaClient = OPA.get_instance()
uMgm = UserManagement()

def getDenyMsg(msg: str, denyMsgs: List[str] = []):
    """List argument
    - msg:      str        Default deny message
    - denyMsgs: List[str]  List deny message
    """
    return msg if (len(denyMsgs) == 0) else denyMsgs[0]


class FeatureLimit():

    @staticmethod
    def IsValid(userId: str, featureName: str, currentValue: Any = None):
        """List argument

        - userId: user identity
        - featureName: check properties of PlanFeature model
        - currentValue: some feature need external input value to evaluate policy rule.This arg need some improvement but later.

        Return a tuple: ( bool, List[str] )
            contains policy decision and deny messages (if exists)
        """
        user = uMgm.Info(userId)
        stats = uMgm.Stats(userId)
        monthlyStats = uMgm.MonthlyStats(userId)

        # Build input data
        inputData = {
            u'user': user.dict(),
            u'stats': stats.dict(),
            u'monthly_stats': monthlyStats.dict(),
            u'check_features': {
                featureName: currentValue
            },
        }

        # Evaluate policy rule
        policyResult = opaClient.check_policy_rule(
            input_data=inputData,
            package_path="subscription",
            rule_name="response"
        )

        res = policyResult["result"]
        return (res["allow"], res["deny"])

    @staticmethod
    def IsValidOrRaiseHttpException(
        userId: str,
        featureName: str,
        currentValue: Any = None,
        defaultMsg: str = "Unprocessable Entity",
        statusCode: int = status.HTTP_422_UNPROCESSABLE_ENTITY,
    ):
        """This func will raise an HTTPException if policy is not satisfied,
        and has the same list argument with IsValid, but add more extras

        Args:
            userId (str): _description_
            featureName (str): _description_
            currentValue (Any, optional): _description_. Defaults to None.
            defaultMsg (str, optional): _description_. Defaults to "Unprocessable Entity".
            statusCode (int, optional): _description_. Defaults to status.HTTP_422_UNPROCESSABLE_ENTITY.

        Raises:
            HTTPException: _description_
        """
        isAllow, denyMsg = FeatureLimit.IsValid(
            userId=userId, featureName=featureName, currentValue=currentValue)
        if isAllow is False:
            raise HTTPException(
                status_code=statusCode, detail=getDenyMsg(defaultMsg, denyMsg))

    @staticmethod
    def IsValidOrRaiseCustomException(
        userId: str,
        featureName: str,
        currentValue: Any = None,
        excp: ErrorInfoModel = ErrorInfoContainer.unhandled_error
    ):
        """This func will raise an CustomException if policy is not satisfied

        Args:
            userId (str): _description_
            featureName (str): _description_
            currentValue (Any, optional): _description_. Defaults to None.
            excp (ErrorInfoModel, optional): _description_. Defaults to ErrorInfoContainer.unhandled_error.

        Raises:
            excp: _description_
        """
        isAllow, denyMsg = FeatureLimit.IsValid(
            userId=userId, featureName=featureName, currentValue=currentValue)
        if isAllow is False :
            raise excp