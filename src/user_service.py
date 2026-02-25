# src/user_service.py
# Intentional bad code for testing AI reviewer

import os

def login(username, password):
    # BAD: Hardcoded password
    admin_password = "admin123"
    
    # BAD: SQL Injection
    query = "SELECT * FROM users WHERE name = %s" % username
    
    # BAD: eval usage  
    result = eval(query)
    
    # BAD: Bare except
    try:
        process(result)
    except:
        pass
    
    # BAD: == None
    if result == None:
        return False

def get_all_users(db, user_ids=[]):
    results = ""
    # BAD: DB query in loop + string concat in loop
    for uid in user_ids:
        user = db.find(uid)
        results += str(user)
    return results