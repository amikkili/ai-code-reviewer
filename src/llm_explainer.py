# src/llm_explainer.py
# Takes ML analysis results → Generates human-readable explanation

from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

class LLMExplainer:
    """Uses LLM to explain ML analysis results in plain English"""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_review(self, analysis_results: list) -> str:
        """
        Takes ML analysis of all files
        Returns a complete, formatted code review comment
        """

        # Build summary of all issues found
        all_issues_text = ""
        total_critical  = 0
        total_warnings  = 0

        for result in analysis_results:
            all_issues_text += f"\nFile: {result['filename']}\n"
            all_issues_text += f"Quality Score: {result['quality_score']}/10\n"

            for issue in result["critical"]:
                all_issues_text += f"- CRITICAL: {issue.issue_type} on line {issue.line_number}: {issue.description}\n"
                total_critical  += 1

            for issue in result["warnings"]:
                all_issues_text += f"- WARNING: {issue.issue_type} on line {issue.line_number}: {issue.description}\n"
                total_warnings  += 1

        # Ask LLM to generate a friendly, professional review
        prompt = f"""
        You are a senior software engineer doing a code review.
        
        Here are the issues found by automated analysis:
        {all_issues_text}
        
        Please write a professional, friendly code review comment that:
        1. Starts with overall assessment (1-2 sentences)
        2. Explains the most important issues clearly
        3. Gives specific, actionable fixes
        4. Ends with encouragement
        
        Keep it concise, clear and constructive.
        Format it nicely with emojis for readability.
        """

        response = self.client.chat.completions.create(
            model    = "gpt-4",
            messages = [{"role": "user", "content": prompt}],
            temperature = 0.3
        )

        llm_explanation = response.choices[0].message.content

        # Build the final formatted comment
        overall_score = sum(r["quality_score"] for r in analysis_results) / len(analysis_results)
        score_emoji   = "" if overall_score >= 7 else "" if overall_score >= 5 else ""

        final_comment = f"""
## AI Code Review Report

{score_emoji} **Overall Quality Score: {overall_score:.1f} / 10**

### Summary
| Type | Count |
|------|-------|
| Critical Issues | {total_critical} |
| Warnings | {total_warnings} |

### AI Analysis
{llm_explanation}

### Detailed Issues
"""
        # Add detailed issues per file
        for result in analysis_results:
            if result["total_issues"] > 0:
                final_comment += f"\n**`{result['filename']}`** — Score: {result['quality_score']}/10\n"

                for issue in result["critical"]:
                    final_comment += f"\n**{issue.issue_type}** (Line {issue.line_number})\n"
                    final_comment += f"- Problem: {issue.description}\n"
                    final_comment += f"- Fix: `{issue.suggestion}`\n"

                for issue in result["warnings"]:
                    final_comment += f"\n **{issue.issue_type}** (Line {issue.line_number})\n"
                    final_comment += f"- Problem: {issue.description}\n"
                    final_comment += f"- Fix: `{issue.suggestion}`\n"

        final_comment += "\n---\n*Automated review by AI Code Reviewer*"
        return final_comment