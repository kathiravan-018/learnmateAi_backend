import os
import time
import json

from google import genai
from dotenv import load_dotenv

from .prompts import LEARNMATE_SYSTEM_PROMPT


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# CREATE GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=os.getenv("GENAI_API_KEY")
)


# ============================================================
# GEMINI REQUEST HELPER
# ============================================================

def generate_with_retry(
    prompt,
    feature_name="Gemini"
):

    models = [
        "gemini-3.5-flash",
        "gemini-3.6-flash",
    ]

    last_error = None

    for model in models:

        for attempt in range(2):

            try:

                print(
                    f"🚀 {feature_name}: "
                    f"Using {model} - Attempt {attempt + 1}/2"
                )

                start_time = time.time()

                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config={}
                )

                elapsed = time.time() - start_time

                print(
                    f"🤖 {feature_name}: "
                    f"{model} responded in {elapsed:.2f} seconds"
                )

                return response

            except Exception as e:

                last_error = e
                error_message = str(e)

                print(
                    f"❌ {feature_name}: "
                    f"{model} failed - {error_message}"
                )

                if "404" in error_message or "NOT_FOUND" in error_message:

                    print(
                        f"❌ {model} is unavailable. "
                        f"Trying next model..."
                    )

                    break

                if attempt < 1:

                    print(
                        "⏳ Temporary failure. "
                        "Retrying in 2 seconds..."
                    )

                    time.sleep(2)

                else:

                    print(
                        f"⚠️ {model} failed twice. "
                        f"Trying next model..."
                    )

    print(
        f"❌ {feature_name}: "
        f"All available models failed."
    )

    raise last_error


# ============================================================
# AI CHAT
# ============================================================

def generate_ai_response(message, history):

    recent_history = history[-6:]

    conversation = ""

    for item in recent_history:

        conversation += (
            f"{item['role']}: "
            f"{item['content']}\n"
        )

    conversation += f"user: {message}\n"

    prompt = f"""
{LEARNMATE_SYSTEM_PROMPT}

conversation:
{conversation}

Answer the student's latest question.

Give a complete explanation suitable for a student.
For a simple question, keep the answer concise but complete.
Use examples when they improve understanding.
Do not unnecessarily repeat the conversation.
Do not stop in the middle of a sentence.
Make sure the answer ends naturally and completely.
"""

    response = generate_with_retry(
        prompt,
        feature_name="AI Chat"
    )

    print("========== GEMINI RESPONSE ==========")
    print(response.text)
    print("========== END RESPONSE =============")

    try:

        print(
            "Finish reason:",
            response.candidates[0].finish_reason
        )

    except Exception as e:

        print(
            "Could not read finish reason:",
            e
        )

    return response.text


# ============================================================
# NOTES GENERATOR
# ============================================================

def generate_notes(topic):

    prompt = f"""
You are LearnMate AI, a student learning assistant.

Generate clear, structured and easy-to-understand
study notes for the given topic.

Topic:
{topic}

Follow this structure:

# Topic

## Definition

Give a simple definition.

## Key Concepts

Explain the important concepts clearly.

## Examples

Give useful examples where appropriate.

## Important Points

List the important points the student should remember.

## Summary

Give a short summary.

Keep the explanation suitable for a student.

Use Markdown formatting.
"""

    response = generate_with_retry(
        prompt,
        feature_name="Notes Generator"
    )

    return response.text




# ============================================================
# QUIZ GENERATOR
# ============================================================

def generate_quiz(topic, previous_questions):

    previous = "\n".join(
        f"- {question}"
        for question in previous_questions
    )

    prompt = f"""
You are LearnMate AI, a quiz generator for students.

Topic:
{topic}

Create exactly 5 multiple-choice questions.

For each question:
- Provide 4 options.
- Provide the correct answer as an index from 0 to 3.
- Provide a short explanation.
- Keep the question and explanation concise.

Do not repeat these previous questions:
{previous}

Return ONLY valid JSON.
Do not use markdown.
Do not add any text outside the JSON.

Required format:

{{
  "questions": [
    {{
      "question": "Question",
      "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "correct_answer": 0,
      "explanation": "Short explanation"
    }}
  ]
}}
"""

    response = generate_with_retry(
        prompt,
        feature_name="Quiz Generator"
    )

    print("========== QUIZ GEMINI RESPONSE ==========")
    print(response.text)
    print("===========================================")

    return json.loads(response.text)
# ============================================================
# CODE EXPLANATION
# ============================================================

def generate_code_explanation(code):

    prompt = f"""
You are LearnMate AI, a programming tutor.

Explain this code clearly and concisely for a student.

Include:
1. What the code does
2. Step-by-step explanation
3. Important concepts
4. Example input/output if useful
5. Short summary

Avoid unnecessary detail.
Keep the explanation focused on the given code.
Do not repeat the code unnecessarily.

Code:
{code}
"""

    response = generate_with_retry(
        prompt,
        feature_name="Code Explanation"
    )

    return response.text