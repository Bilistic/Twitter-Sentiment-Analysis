import pymongo
from pymongo import MongoClient
import time
import datetime


class DAO:

    def __init__(self, host="localhost", port=27017, database="test", collection="test_collection"):
        retries = 5
        while True:
            try:
                self.__client = MongoClient(host, port)
                self.__database = self.__client[database]
                self.__collection = self.__database[collection]
                self.__posts = self.__collection.posts
                break
            except pymongo.errors.ConnectionFailure as e:
                if retries == 0:
                    raise e
                retries -= 1
                time.sleep(0.5)
        pass

    def save(self, data):
        self.__posts.insert_one(data)
        pass

    def get_by_time(self, time_stamp):
        return list(self.__posts.find(
            {"creation_date": {"$gt": datetime.datetime.utcnow() - datetime.timedelta(minutes=time_stamp)}}))
