
import streamlit as st
from openai import OpenAI
import os
import re

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_ai_feedback(task_outline: str, submission_text: str, categories: dict, evaluation_style: str = "balanced") -> str:
    if len(submission_text) > 6000:
        parts = submission_text.split('\n--- Page')
        truncated = parts[0]
        for part in parts[1:]:
            if len(truncated + part) < 6000:
                truncated += '\n--- Page' + part
            else:
                break
        submission_text = truncated + "\n\n[Content truncated for analysis...]"

    style_instructions = {
        "strict": "Be highly critical and set very high standards.",
        "balanced": "Provide fair, constructive evaluation.",
        "encouraging": "Focus on positive aspects while still providing honest feedback."
    }

    category_list = "\n".join([f"{i+1}. {cat}" for i, cat in enumerate(categories.keys())])

    prompt = f"""
You are an expert evaluator with a {evaluation_style} approach. {style_instructions[evaluation_style]}

EVALUATION TASK:
{task_outline}

STUDENT SUBMISSION:
{submission_text}

Please evaluate the submission across these categories (rate each 0-10):
{category_list}

For each category, provide:
- A numerical score (0-10)
- 2-3 sentences explaining your reasoning
- One specific suggestion for improvement

Format:
Category Name: X/10 - Explanation. Improvement suggestion.

Then provide:
Overall Assessment:
Actionable Next Steps:
"""

    try:
        with st.spinner("AI is analyzing your work..."):
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            )
        return response.choices[0].message.content
    except Exception as e:
        return f"ERROR: OpenAI API issue - {str(e)}"

def parse_scores_enhanced(ai_response: str, categories: dict) -> dict:
    scores = {}
    for category in categories.keys():
        pattern = rf"{re.escape(category)}:\s*(\d{{1,2}})\/10\s*[-–]\s*(.+?)(?=\n\w+:|Overall Assessment:|Actionable Next Steps:|$)"
        match = re.search(pattern, ai_response, re.DOTALL | re.IGNORECASE)
        if match:
            score = min(10, max(0, int(match.group(1))))
            explanation = match.group(2).strip()
            scores[category] = (score, explanation)
        else:
            scores[category] = (5, "Score could not be parsed.")
    return scores

def extract_enhanced_feedback(ai_response: str) -> dict:
    feedback = {}
    overall_match = re.search(r"Overall Assessment:\s*(.*?)(?=Actionable Next Steps:|$)", ai_response, re.DOTALL)
    feedback["overall"] = overall_match.group(1).strip() if overall_match else "No overall assessment found."

    action_match = re.search(r"Actionable Next Steps:\s*(.*?)$", ai_response, re.DOTALL)
    if action_match:
        actions = re.findall(r"\d+\.\s*(.+?)(?=\n\d+\.|$)", action_match.group(1), re.DOTALL)
        feedback["actions"] = [action.strip() for action in actions]
    else:
        feedback["actions"] = ["Review the detailed feedback above."]
    return feedback
