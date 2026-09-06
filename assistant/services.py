import os
import time
import json

from google import genai
from google.genai import types
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
    system_instruction=None,
    response_mime_type=None,
    response_schema=None
):

    # Fast models
    models = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ]

    last_error = None

    # Build Gemini configuration
    config_args = {}

    if system_instruction:
        config_args["system_instruction"] = system_instruction

    if response_mime_type:
        config_args["response_mime_type"] = response_mime_type

    if response_schema:
        config_args["response_schema"] = response_schema

    config = (
        types.GenerateContentConfig(**config_args)
        if config_args
        else None
    )

    # ========================================================
    # TRY MODELS
    # ========================================================

    for model in models:

        try:

            print(
                f"🚀 {feature_name}: "
                f"Using {model}"
            )

            start_time = time.time()

            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=config
            )

            elapsed = time.time() - start_time

            print(
                f"🤖 {feature_name}: "
                f"{model} responded in "
                f"{elapsed:.2f} seconds"
            )

            return response

        except Exception as e:

            last_error = e

            print(
                f"❌ {feature_name}: "
                f"{model} failed: {str(e)}"
            )

            print(
                f"⚠️ Trying next model..."
            )

    # ========================================================
    # ALL MODELS FAILED
    # ========================================================

    print(
        f"❌ {feature_name}: "
        f"All available models failed."
    )

    raise last_error


# ============================================================
# AI CHAT
# ============================================================

def generate_ai_response(message, history):

    # Keep only recent conversation
    recent_history = history[-4:]

    conversation_lines = []

    for item in recent_history:

        conversation_lines.append(
            f"{item['role']}: {item['content']}"
        )

    conversation_lines.append(
        f"user: {message}"
    )

    conversation = "\n".join(
        conversation_lines
    )

    prompt = f"""
Conversation:

{conversation}

Answer the student's latest question.

Give a clear and complete answer.
Keep simple questions concise.
Use an example when useful.
Do not repeat unnecessary information.
"""

    response = generate_with_retry(
        prompt,
        feature_name="AI Chat",
        system_instruction=LEARNMATE_SYSTEM_PROMPT
    )

    return response.text


# ============================================================
# NOTES GENERATOR
# ============================================================

def generate_notes(topic):

    system_prompt = """
You are LearnMate AI, a student learning assistant.
Create clear and easy-to-understand study notes.
"""

    prompt = f"""
Create study notes about:

{topic}

Use this structure:

# {topic}

## Definition

## Key Concepts

## Examples

## Important Points

## Summary

Keep the explanation clear and reasonably concise.
Use Markdown.
"""

    response = generate_with_retry(
        prompt,
        feature_name="Notes Generator",
        system_instruction=system_prompt
    )

    return response.text


# ============================================================
# QUIZ SCHEMA
# ============================================================

QUIZ_SCHEMA = {
    "type": "object",
    "properties": {

        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {

                    "question": {
                        "type": "string"
                    },

                    "options": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },

                    "correct_answer": {
                        "type": "integer"
                    },

                    "explanation": {
                        "type": "string"
                    }

                },
                "required": [
                    "question",
                    "options",
                    "correct_answer",
                    "explanation"
                ]
            }
        }

    },

    "required": [
        "questions"
    ]
}


# ============================================================
# QUIZ GENERATOR
# ============================================================

def generate_quiz(topic, previous_questions):

    # Limit previous questions
    # so the prompt doesn't become unnecessarily large.
    previous_questions = previous_questions[-10:]

    if previous_questions:

        previous = "\n".join(
            f"- {question}"
            for question in previous_questions
        )

    else:

        previous = "None"

    system_prompt = """
You are LearnMate AI, a fast quiz generator for students.
Return only the requested JSON structure.
"""

    prompt = f"""
Create exactly 5 multiple-choice questions about:

{topic}

Requirements:

- Exactly 5 questions.
- Exactly 4 options per question.
- correct_answer must be 0, 1, 2, or 3.
- Include a short explanation.
- Questions must be different.
- Do not repeat previous questions.
- Keep questions and explanations concise.

Previous questions:

{previous}
"""

    response = generate_with_retry(
        prompt,
        feature_name="Quiz Generator",
        system_instruction=system_prompt,
        response_mime_type="application/json",
        response_schema=QUIZ_SCHEMA
    )

    print(
        "========== QUIZ GEMINI RESPONSE =========="
    )

    print(response.text)

    print(
        "==========================================="
    )

    return json.loads(response.text)


# ============================================================
# CODE EXPLANATION
# ============================================================

def generate_code_explanation(code):

    system_prompt = """
You are LearnMate AI, a concise programming tutor.
Explain code clearly for students.
"""

    prompt = f"""
Explain this code:

{code}

Include:

1. What it does
2. Step-by-step explanation
3. Important concepts
4. Example input/output if useful
5. Short summary

Avoid unnecessary detail.
Do not repeat the entire code.
"""

    response = generate_with_retry(
        prompt,
        feature_name="Code Explanation",
        system_instruction=system_prompt
    )

    return response.text