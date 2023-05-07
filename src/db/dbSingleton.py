import redis.asyncio as redis

from src.db import fireStoreDB

class DBSingleton:
    __instance__ = None

    def __init__(self):
        """ Constructor.
        """
        if DBSingleton.__instance__ is None:
            DBSingleton.__instance__ = redis.from_url("redis://localhost:6379", encoding="utf-8", decode_responses=True)

    @staticmethod
    def get_instance():
        """ Static method to fetch the current instance.
        """
        if not DBSingleton.__instance__:
            DBSingleton()
        return DBSingleton.__instance__

class FirestoreDBSingleton:
    __instance__ = None

    def __init__(self):
        """ Constructor.
        """
        if FirestoreDBSingleton.__instance__ is None:
            FirestoreDBSingleton.__instance__ = fireStoreDB.FireStoreDB().getInstance()

    @staticmethod
    def get_instance():
        """ Static method to fetch the current instance.
        """
        if not FirestoreDBSingleton.__instance__:
            FirestoreDBSingleton()
        return FirestoreDBSingleton.__instance__