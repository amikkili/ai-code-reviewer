# This is your ML engine — it analyzes code and finds issues

import re
import ast
from dataclasses import dataclass
from typing import List

# ─────────────────────────────────────
# Data structure for each issue found
# ─────────────────────────────────────
@dataclass
class CodeIssue:
    severity:    str    # CRITICAL / WARNING / INFO
    issue_type:  str    # What kind of issue
    description: str    # What is the issue
    line_number:  int   # Where in the code
    suggestion:  str    # How to fix it

class MLCodeAnalyzer:
    """
    ML-powered code analyzer
    Detects bugs, security issues, and code quality problems
    """

    def analyze(self, code: str, filename: str) -> dict:
        """
        Main analysis function
        Takes code as input → Returns issues + quality score
        """
        issues = []

        # Run all checks
        issues.extend(self._check_security_issues(code))
        issues.extend(self._check_code_quality(code))
        issues.extend(self._check_python_best_practices(code))
        issues.extend(self._check_performance_issues(code))

        # Calculate quality score
        quality_score = self._calculate_score(issues, code)

        return {
            "filename":      filename,
            "quality_score": quality_score,
            "total_issues":  len(issues),
            "critical":      [i for i in issues if i.severity == "CRITICAL"],
            "warnings":      [i for i in issues if i.severity == "WARNING"],
            "info":          [i for i in issues if i.severity == "INFO"],
            "issues":        issues
        }

    # ─────────────────────────────────────
    # CHECK 1: Security Issues
    # ─────────────────────────────────────
    def _check_security_issues(self, code: str) -> List[CodeIssue]:
        issues = []
        lines = code.split("\n")

        for i, line in enumerate(lines, 1):

            # Check for hardcoded passwords
            if re.search(r'password\s*=\s*["\'](.+)["\']', line, re.IGNORECASE):
                issues.append(CodeIssue(
                    severity    = "CRITICAL",
                    issue_type  = "Hardcoded Password",
                    description = f"Hardcoded password found on line {i}",
                    line_number = i,
                    suggestion  = "Use environment variables: os.getenv('PASSWORD')"
                ))

            # Check for SQL injection risk
            if re.search(r'execute\s*\(\s*["\'].*%s.*["\']', line):
                issues.append(CodeIssue(
                    severity    = "CRITICAL",
                    issue_type  = "SQL Injection Risk",
                    description = f"Direct string formatting in SQL query on line {i}",
                    line_number = i,
                    suggestion  = "Use parameterized queries: cursor.execute(sql, (params,))"
                ))

            # Check for hardcoded API keys
            if re.search(r'api_key\s*=\s*["\'][a-zA-Z0-9]{20,}["\']', line, re.IGNORECASE):
                issues.append(CodeIssue(
                    severity    = "CRITICAL",
                    issue_type  = "Exposed API Key",
                    description = f"Hardcoded API key found on line {i}",
                    line_number = i,
                    suggestion  = "Use environment variables: os.getenv('API_KEY')"
                ))

            # Check for eval() usage
            if re.search(r'\beval\s*\(', line):
                issues.append(CodeIssue(
                    severity    = "CRITICAL",
                    issue_type  = "Dangerous eval() Usage",
                    description = f"eval() is dangerous and can execute malicious code — line {i}",
                    line_number = i,
                    suggestion  = "Avoid eval(). Use ast.literal_eval() for safe evaluation"
                ))

        return issues

    # ─────────────────────────────────────
    # CHECK 2: Code Quality Issues
    # ─────────────────────────────────────
    def _check_code_quality(self, code: str) -> List[CodeIssue]:
        issues = []
        lines  = code.split("\n")

        for i, line in enumerate(lines, 1):

            # Check line too long (PEP8 standard = max 79 chars)
            if len(line) > 120:
                issues.append(CodeIssue(
                    severity    = "INFO",
                    issue_type  = "Long Line",
                    description = f"Line {i} is {len(line)} characters (recommended max: 120)",
                    line_number = i,
                    suggestion  = "Break long lines for better readability"
                ))

            # Check for print statements in production code
            if re.search(r'^\s*print\s*\(', line):
                issues.append(CodeIssue(
                    severity    = "INFO",
                    issue_type  = "Print Statement Found",
                    description = f"print() found on line {i} — use logging instead",
                    line_number = i,
                    suggestion  = "Replace with: import logging → logging.info('message')"
                ))

            # Check for TODO comments
            if re.search(r'#\s*(TODO|FIXME|HACK|XXX)', line, re.IGNORECASE):
                issues.append(CodeIssue(
                    severity    = "WARNING",
                    issue_type  = "Unresolved TODO",
                    description = f"Unresolved TODO/FIXME comment on line {i}",
                    line_number = i,
                    suggestion  = "Resolve this before merging to main branch"
                ))

        # Check for missing docstrings in functions
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not (node.body and isinstance(node.body[0], ast.Expr)
                            and isinstance(node.body[0].value, ast.Constant)):
                        issues.append(CodeIssue(
                            severity    = "INFO",
                            issue_type  = "Missing Docstring",
                            description = f"Function '{node.name}' has no docstring",
                            line_number = node.lineno,
                            suggestion  = f'Add docstring: def {node.name}():\n    """What this function does"""'
                        ))
        except SyntaxError:
            pass  # Skip AST check if code has syntax errors

        return issues

    # ─────────────────────────────────────
    # CHECK 3: Python Best Practices
    # ─────────────────────────────────────
    def _check_python_best_practices(self, code: str) -> List[CodeIssue]:
        issues = []
        lines  = code.split("\n")

        for i, line in enumerate(lines, 1):

            # Check for bare except
            if re.search(r'except\s*:', line):
                issues.append(CodeIssue(
                    severity    = "WARNING",
                    issue_type  = "Bare Except Clause",
                    description = f"Catching ALL exceptions is bad practice — line {i}",
                    line_number = i,
                    suggestion  = "Specify exception: except ValueError: or except Exception as e:"
                ))

            # Check for mutable default arguments
            if re.search(r'def\s+\w+\s*\(.*=\s*(\[\]|\{\})', line):
                issues.append(CodeIssue(
                    severity    = "WARNING",
                    issue_type  = "Mutable Default Argument",
                    description = f"Using mutable default argument on line {i} causes bugs",
                    line_number = i,
                    suggestion  = "Use None as default: def func(items=None): items = items or []"
                ))

            # Check for == None instead of is None
            if re.search(r'==\s*None', line):
                issues.append(CodeIssue(
                    severity    = "INFO",
                    issue_type  = "Incorrect None Comparison",
                    description = f"Use 'is None' instead of '== None' on line {i}",
                    line_number = i,
                    suggestion  = "Replace '== None' with 'is None'"
                ))

        return issues

    # ─────────────────────────────────────
    # CHECK 4: Performance Issues
    # ─────────────────────────────────────
    def _check_performance_issues(self, code: str) -> List[CodeIssue]:
        issues = []
        lines  = code.split("\n")

        in_loop    = False
        loop_lines = []

        for i, line in enumerate(lines, 1):

            # Track if we're inside a loop
            if re.search(r'^\s*(for|while)\s+', line):
                in_loop    = True
                loop_lines = []

            # Check for DB queries inside loops (N+1 problem)
            if in_loop and re.search(r'\.(find|query|execute|select|get)\s*\(', line):
                issues.append(CodeIssue(
                    severity    = "WARNING",
                    issue_type  = "Database Query in Loop",
                    description = f"DB query inside loop on line {i} — causes N+1 problem!",
                    line_number = i,
                    suggestion  = "Move query outside loop, fetch all data at once"
                ))

            # Check for string concatenation in loops
            if in_loop and re.search(r'\+=\s*["\']', line):
                issues.append(CodeIssue(
                    severity    = "INFO",
                    issue_type  = "String Concat in Loop",
                    description = f"String concatenation in loop on line {i} is slow",
                    line_number = i,
                    suggestion  = "Use list.append() then ''.join() for better performance"
                ))

        return issues

    # ─────────────────────────────────────
    # CALCULATE QUALITY SCORE
    # ─────────────────────────────────────
    def _calculate_score(self, issues: list, code: str) -> float:
        """
        Calculate code quality score out of 10
        based on issues found
        """
        base_score = 10.0

        for issue in issues:
            if issue.severity == "CRITICAL":
                base_score -= 2.0      # -2 for each critical issue
            elif issue.severity == "WARNING":
                base_score -= 1.0      # -1 for each warning
            elif issue.severity == "INFO":
                base_score -= 0.3      # -0.3 for each info

        return max(0.0, round(base_score, 1))   # Minimum score is 0