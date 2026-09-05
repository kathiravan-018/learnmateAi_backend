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
    feature_name="Gemini",
    max_output_tokens=800
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
                    config={
                        "max_output_tokens": max_output_tokens,
                        "temperature": 0.7,
                    }
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

Give a clear and concise answer suitable for voice learning.
Avoid unnecessary detail unless the user asks for a detailed explanation.
"""

    response = generate_with_retry(
        prompt,
        feature_name="AI Chat",
        max_output_tokens=500
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
        feature_name="Notes Generator",
        max_output_tokens=1200
    )

    return response.text


# ============================================================
# QUIZ GENERATOR
# ============================================================

def generate_quiz(topic, previous_questions):

    previous = ""

    for question in previous_questions:

        previous += f"- {question}\n"

    prompt = f"""
You are LearnMate AI, a student quiz generator.

Create a quiz for the following topic:

{topic}

Generate exactly 5 multiple-choice questions.

Each question must contain:

- question
- exactly 4 options
- correct_answer
- explanation

Previously generated questions:

{previous}

Generate a completely new quiz.

Do NOT repeat any of the previous questions.

Change the question wording, concepts,
examples, and options where possible.

Return ONLY valid JSON.

Use this structure:

{{
    "questions": [
        {{
            "question": "Question text",
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],
            "correct_answer": 0,
            "explanation": "Explanation"
        }}
    ]
}}
"""

    response = generate_with_retry(
    prompt,
    feature_name="Quiz Generator",
    max_output_tokens=1000
)

    return json.loads(response.text)


# ============================================================
# CODE EXPLANATION
# ============================================================

def generate_code_explanation(code):

    prompt = f"""
You are LearnMate AI, a programming learning assistant.

Explain the following code in a simple way for a student.

Your explanation should include:

1. What the code does
2. Step-by-step explanation
3. Important concepts used
4. Example input and output if applicable
5. A simple summary

Code:

{code}
"""

    response = generate_with_retry(
    prompt,
    feature_name="Code Explanation",
    max_output_tokens=1000
)

    return response.text