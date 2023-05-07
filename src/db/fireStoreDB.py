from enum import Enum
import json
from typing import Any
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud import firestore as gcFirestore
from ..config.config import settings


class ListCollection(Enum):
    BASE = u'base'
    EVENTS = u'events'
    STATS = u'stats'
    ENTERPRISE = u'enterprise'

class FireStoreDB(object):
    def __call__(self):
        self.app = self.getInstance()

    def getInstance(self) -> gcFirestore.Client:
        jsonCred = json.loads(settings.DB.FireStore.Credentials)
        cred = credentials.Certificate(jsonCred)
        app = firebase_admin.initialize_app(cred, name='firestore_db')
        return firestore.client(app)