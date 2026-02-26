# src/payment_service.py
# Bad code for AI review testing

import os

def process_payment(user_id, amount):
    # BAD: Hardcoded API key
    api_key = "sk-live-abcdefghijklmnop123456"
    
    # BAD: Hardcoded password
    db_password = "admin123"
    
    # BAD: SQL Injection
    query = "SELECT * FROM payments WHERE user = %s" % user_id
    
    # BAD: eval usage
    result = eval(query)
    
    if result == None:
        return False

def calculate_fees(transactions=[]):
    total = ""
    for t in transactions:
        # BAD: DB query in loop
        record = db.find(t)
        # BAD: String concat in loop  
        total += str(record)
    
    try:
        return float(total)
    except:
        pass