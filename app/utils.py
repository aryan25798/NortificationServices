# app/utils.py

def is_valid_notification_type(ntype: str) -> bool:
    return ntype in ["email", "sms", "in-app"]
