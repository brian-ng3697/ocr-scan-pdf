import json
import os
import pathlib

from opa_client.opa import OpaClient

from ..config.config import settings
from ..models.planFeature import FREE_PLAN_FEATURE, PREMIUM_PLAN_FEATURE, BUSSINESS_PLAN_FEATURE


class OPA:
    __instance__ = None

    def __init__(self):
        """ Constructor.
        """
        currentPath = str(pathlib.Path(__file__).parent.resolve())

        if OPA.__instance__ is None:
            opaClient = OpaClient(
                host=settings.OPA.Host,
                port=settings.OPA.Port,
                version="v1",
                # ssl=True,
                # cert="/your/certificate/file/path/mycert.crt",
            )

            opaClient.check_connection()

            # Load policy and data for subcription
            fp = currentPath + "/policies/subscription.rego"
            opaClient.update_opa_policy_fromfile(
                filepath=fp, endpoint="subscription")

            # load subscription data
            opaClient.update_or_create_opa_data({
                "plan_features": {
                    FREE_PLAN_FEATURE.name: FREE_PLAN_FEATURE.dict(),
                    PREMIUM_PLAN_FEATURE.name: PREMIUM_PLAN_FEATURE.dict(),
                    BUSSINESS_PLAN_FEATURE.name: BUSSINESS_PLAN_FEATURE.dict(),
                }
            }, "subscription")

            OPA.__instance__ = opaClient

    @staticmethod
    def get_instance():
        """ Static method to fetch the current instance.
        """
        if not OPA.__instance__:
            OPA()
        return OPA.__instance__
