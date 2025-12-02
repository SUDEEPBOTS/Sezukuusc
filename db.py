# db.py

import pymongo
from pymongo import MongoClient
from config import MONGO_URI
import certifi

ca = certifi.where()

try:
    client = MongoClient(MONGO_URI, tlsCAFile=ca)
    db = client["sezukuu_security"]

    print("✅ MongoDB Connected Successfully")

except Exception as e:
    print("❌ MongoDB Connection Failed:", e)
    db = None
