# src/llm_explainer.py — Handle no issues + better error handling

from groq import Groq
from dotenv import load_dotenv
import os
import traceback

load_dotenv()

class LLMExplainer:

    def __init__(self):
        self.client = None

    def _get_client(self):
        if self.client is None:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("❌ GROQ_API_KEY is not set in environment variables!")
            self.client = Groq(api_key=api_key)
            print("Connected to Groq!")
        return self.client

    def generate_review(self, analysis_results: list) -> str:
        try:
            # Calculate totals
            total_critical = sum(len(r["critical"]) for r in analysis_results)
            total_warnings = sum(len(r["warnings"]) for r in analysis_results)
            total_info     = sum(len(r["info"])     for r in analysis_results)
            overall_score  = sum(r["quality_score"] for r in analysis_results) / len(analysis_results)
            score_emoji    = "@" if overall_score >= 7 else "#" if overall_score >= 5 else "*"

            # ─────────────────────────────────────
            # If NO issues found — return clean result
            # No need to call LLM!
            # ─────────────────────────────────────
            if total_critical == 0 and total_warnings == 0 and total_info == 0:
                return f"""##  AI Code Review Report

{score_emoji} **Overall Quality Score: {overall_score:.1f} / 10**

---

### Great News!
No issues found in this PR. The code looks clean and follows best practices!

**Files Reviewed:**
{chr(10).join(f"- `{r['filename']}`" for r in analysis_results)}

---
* Automated review by AI Code Reviewer using Groq LLaMA3*"""

            # ─────────────────────────────────────
            # Build issues summary for LLM
            # ─────────────────────────────────────
            all_issues_text = ""
            for result in analysis_results:
                all_issues_text += f"\nFile: {result['filename']}\n"
                all_issues_text += f"Quality Score: {result['quality_score']}/10\n"

                for issue in result["critical"]:
                    all_issues_text += f"- CRITICAL: {issue.issue_type} on line {issue.line_number}: {issue.description}\n"

                for issue in result["warnings"]:
                    all_issues_text += f"- WARNING: {issue.issue_type} on line {issue.line_number}: {issue.description}\n"

                for issue in result["info"]:
                    all_issues_text += f"- INFO: {issue.issue_type} on line {issue.line_number}: {issue.description}\n"

            print(f"📊 Issues found — Critical: {total_critical}, Warnings: {total_warnings}, Info: {total_info}")

            # ─────────────────────────────────────
            # Call Groq LLM
            # ─────────────────────────────────────
            print(" Calling Groq API...")
            client   = self._get_client()
            response = client.chat.completions.create(
                model       = "llama3-8b-8192",
                messages    = [{
                    "role":    "user",
                    "content": f"""You are a senior software engineer doing a code review.

Here are the issues found:
{all_issues_text}

Write a professional, friendly code review that:
1. Gives overall assessment in 2 sentences
2. Explains the critical issues clearly  
3. Gives specific actionable fixes
4. Ends with encouragement

Use emojis. Be concise and constructive."""
                }],
                temperature = 0.3,
                max_tokens  = 500
            )

            llm_explanation = response.choices[0].message.content
            print("Groq response received!")

            # ─────────────────────────────────────
            # Build final formatted comment
            # ─────────────────────────────────────
            final_comment = f"""## AI Code Review Report

{score_emoji} **Overall Quality Score: {overall_score:.1f} / 10**

---

### 📊 Summary
| Type | Count |
|------|-------|
|  Critical Issues | {total_critical} |
|  Warnings | {total_warnings} |
|  Info | {total_info} |

---

###  AI Analysis
{llm_explanation}

---

###  Detailed Issues
"""
            # Add per-file details
            for result in analysis_results:
                if result["total_issues"] > 0:
                    final_comment += f"\n**`{result['filename']}`** — Score: {result['quality_score']}/10\n"

                    for issue in result["critical"]:
                        final_comment += f"\n **{issue.issue_type}** (Line {issue.line_number})\n"
                        final_comment += f"- Problem: {issue.description}\n"
                        final_comment += f"- Fix: `{issue.suggestion}`\n"

                    for issue in result["warnings"]:
                        final_comment += f"\n **{issue.issue_type}** (Line {issue.line_number})\n"
                        final_comment += f"- Problem: {issue.description}\n"
                        final_comment += f"- Fix: `{issue.suggestion}`\n"

                    for issue in result["info"]:
                        final_comment += f"\n **{issue.issue_type}** (Line {issue.line_number})\n"
                        final_comment += f"- Problem: {issue.description}\n"
                        final_comment += f"- Fix: `{issue.suggestion}`\n"

            final_comment += "\n---\n* Automated review by AI Code Reviewer using Groq LLaMA3*"
            return final_comment

        except Exception as e:
            error_details = traceback.format_exc()
            print(f"❌ LLM Explainer Error: {error_details}")
            # Return a basic comment even if LLM fails
            return f"""##  AI Code Review Report

**AI explanation unavailable** — but here are the raw findings:

**Overall Score:** {overall_score:.1f}/10
**Critical Issues:** {total_critical}
**Warnings:** {total_warnings}

*Error details logged for debugging.*
---
* Automated review by AI Code Reviewer*"""