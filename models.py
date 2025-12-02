from pymongo import MongoClient
from datetime import datetime

client = MongoClient()
db = client["sezukuu_security"]

# ---------------- USERS ----------------

def get_user(user_id):
    user = db.users.find_one({"user_id": user_id})
    if not user:
        user = {
            "user_id": user_id,
            "total_appeals_accepted": 0,
            "total_bans": 0,
            "verified": False,
            "profile": {},
            "created": datetime.utcnow()
        }
        db.users.insert_one(user)
    return user


def increment_ban(user_id):
    db.users.update_one(
        {"user_id": user_id},
        {"$inc": {"total_bans": 1}}
    )


def accept_appeal(user_id):
    db.users.update_one(
        {"user_id": user_id},
        {"$inc": {"total_appeals_accepted": 1}}
    )


def set_verified(user_id, status=True):
    db.users.update_one(
        {"user_id": user_id},
        {"$set": {"verified": status}}
    )


def save_profile(user_id, data):
    db.users.update_one(
        {"user_id": user_id},
        {"$set": {"profile": data}}
    )


# ---------------- GROUPS ----------------

def get_group(chat_id):
    group = db.groups.find_one({"chat_id": chat_id})
    if not group:
        group = {
            "chat_id": chat_id,
            "rules": "No rules set.",
            "welcome_enabled": True,
            "logger_enabled": True,
            "created": datetime.utcnow()
        }
        db.groups.insert_one(group)
    return group


# ---------------- MULTI-GC BAN/APPEAL ----------------

def add_ban_record(user_id, chat_id, reason):
    db.bans.insert_one({
        "user_id": user_id,
        "chat_id": chat_id,
        "reason": reason,
        "time": datetime.utcnow(),
        "appeal_status": "pending"
    })


def get_pending_appeals(user_id):
    return list(
        db.bans.find({
            "user_id": user_id,
            "appeal_status": "pending"
        })
    )


def approve_appeal(user_id, chat_id):
    db.bans.update_one(
        {"user_id": user_id, "chat_id": chat_id},
        {"$set": {"appeal_status": "approved"}}
    )


def reject_appeal(user_id, chat_id):
    db.bans.update_one(
        {"user_id": user_id, "chat_id": chat_id},
        {"$set": {"appeal_status": "rejected"}}
    )


# ---------------- LOGGER EVENTS ----------------

def log_event(type, data):
    db.logs.insert_one({
        "type": type,
        "data": data,
        "time": datetime.utcnow()
    })
