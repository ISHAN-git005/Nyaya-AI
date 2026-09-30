import os
import datetime
from tinydb import TinyDB, Query

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "nyaya_ai_db"

mongo_client = None
mongo_db = None
use_mongo = False

try:
    from pymongo import MongoClient
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1500)
    mongo_client.server_info()  # Triggers exception if unreachable
    mongo_db = mongo_client[DB_NAME]
    use_mongo = True
    print("[DB INFO] Connected to MongoDB.")
except Exception:
    print("[DB INFO] MongoDB unavailable. Falling back to TinyDB (local_db.json).")
    tinydb = TinyDB("local_db.json")

def save_record(collection_name: str, data: dict):
    data["timestamp"] = datetime.datetime.utcnow().isoformat()
    if use_mongo and mongo_db is not None:
        try:
            mongo_db[collection_name].insert_one(data.copy())
            return True
        except Exception:
            pass
    table = tinydb.table(collection_name)
    table.insert(data)
    return True

def fetch_recent(collection_name: str, limit: int = 10):
    if use_mongo and mongo_db is not None:
        try:
            records = list(mongo_db[collection_name].find({}, {"_id": 0}).sort("timestamp", -1).limit(limit))
            return records
        except Exception:
            pass
    table = tinydb.table(collection_name)
    all_rows = table.all()
    return sorted(all_rows, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]