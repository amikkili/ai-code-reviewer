# test_local.py — Test your ML analyzer immediately!

from src.ml_analyzer import MLCodeAnalyzer

# Sample BAD code to test with (has multiple issues!)
bad_code = '''
import os

def get_user(user_id):
    password = "admin123"
    api_key = "sk-abcdefghijklmnopqrstuvwxyz123456"
    
    query = "SELECT * FROM users WHERE id = %s" % user_id
    cursor.execute(query)
    
    for user in users:
        result = db.find(user_id)
        print(result)
    
    try:
        process_user()
    except:
        pass
    
    if user == None:
        return None

def calculate(items=[]):
    total = ""
    for item in items:
        total += str(item)
    return total
'''

# Run the analyzer!
analyzer = MLCodeAnalyzer()
result   = analyzer.analyze(bad_code, "user_service.py")

# Show results
print(f"\n{'='*50}")
print(f"CODE QUALITY SCORE: {result['quality_score']} / 10")
print(f"{'='*50}")
print(f"Total Issues Found: {result['total_issues']}")
print(f"Critical: {len(result['critical'])}")
print(f"Warnings: {len(result['warnings'])}")
print(f"Info:     {len(result['info'])}")

print(f"\n{'='*50}")
print("CRITICAL ISSUES:")
print(f"{'='*50}")
for issue in result['critical']:
    print(f"\n  Issue:      {issue.issue_type}")
    print(f"  Line:       {issue.line_number}")
    print(f"  Problem:    {issue.description}")
    print(f"  Fix:        {issue.suggestion}")

print(f"\n{'='*50}")
print("WARNINGS:")
print(f"{'='*50}")
for issue in result['warnings']:
    print(f"\n  Issue:      {issue.issue_type}")
    print(f"  Line:       {issue.line_number}")
    print(f"  Problem:    {issue.description}")
    print(f"  Fix:        {issue.suggestion}")