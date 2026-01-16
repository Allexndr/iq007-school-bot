import os
import json
from datetime import datetime, timedelta

STUDENT_PASSWORD_PATH = "/home/funarick/IQ007_BOT/app/student_passwords.json"
MAX_PASSWORDS_PER_USER = 4
RESET_INTERVAL_DAYS = 30

def initialize_user_data():
    if not os.path.exists(STUDENT_PASSWORD_PATH):
        with open(STUDENT_PASSWORD_PATH, 'w') as f:
            json.dump({
                "logins_passwords": [],
                "user_requests": {},
                "total_issued_passwords": 0,
                "last_reset_date": datetime.now().isoformat()
            }, f, indent=4)
    else:
        with open(STUDENT_PASSWORD_PATH, 'r') as f:
            data = json.load(f)
        
        if "user_requests" not in data:
            data["user_requests"] = {}
        if not data.get("last_reset_date"):
            data["last_reset_date"] = datetime.now().isoformat()

        with open(STUDENT_PASSWORD_PATH, 'w') as f:
            json.dump(data, f, indent=4)

def can_issue_password(user_id):
    with open(STUDENT_PASSWORD_PATH, 'r') as f:
        data = json.load(f)
    
    user_requests = data["user_requests"].get(str(user_id), {"count": 0, "last_request_date": None})
    
    if user_requests["last_request_date"]:
        last_request_date = datetime.fromisoformat(user_requests["last_request_date"])
        if datetime.now() - last_request_date > timedelta(days=RESET_INTERVAL_DAYS):
            user_requests["count"] = 0  # Сброс счетчика после интервала
    
    if user_requests["count"] < MAX_PASSWORDS_PER_USER:
        user_requests["count"] += 1
        user_requests["last_request_date"] = datetime.now().isoformat()
        data["user_requests"][str(user_id)] = user_requests

        with open(STUDENT_PASSWORD_PATH, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    else:
        return False

def get_password():
    with open(STUDENT_PASSWORD_PATH, 'r') as f:
        data = json.load(f)
    
    for entry in data["logins_passwords"]:
        if not entry["issued"]:
            entry["issued"] = True
            entry["issued_count"] += 1
            entry["last_reset_date"] = datetime.now().isoformat()
            data["total_issued_passwords"] += 1
            
            with open(STUDENT_PASSWORD_PATH, 'w') as f:
                json.dump(data, f, indent=4)
            return entry
    
    return None
