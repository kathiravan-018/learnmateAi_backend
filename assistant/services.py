import os
import time

from google import genai
from dotenv import load_dotenv

from .prompts import LEARNMATE_SYSTEM_PROMPT


# Load environment variables
load_dotenv()


# Create Gemini client
client = genai.Client(
    api_key=os.getenv("GENAI_API_KEY")
)


def generate_ai_response(message , history):

    conversation = ""
    
    for item in history:
        conversation += f"{item['role']}: {item['content']}\n"
    
    conversation += f"user: {message}\n"

    start_time = time.time()

    print("🚀 Sending request to Gemini...")

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=f"""
        {LEARNMATE_SYSTEM_PROMPT}

        conversation:
        {conversation}
        """
        )

    elapsed = time.time() - start_time

    print(f"🤖 Gemini took: {elapsed:.2f} seconds")

    return response.text

def generate_notes(topic):

    start_time = time.time()

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=f"""
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
            
            )
    elapsed = time.time()-start_time
    print(
        f"📝 Notes generated in: {elapsed:.2f} seconds"
    )

    return response.text

import json


def generate_quiz(topic, previous_questions):

    start_time = time.time()

    previous = ""

    for question in previous_questions:
        previous += f"- {question}\n"

    print("🧠 Generating quiz for:", topic)

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=f"""
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
    )

    elapsed = time.time() - start_time

    print(
        f"🧠 Quiz generated in: {elapsed:.2f} seconds"
    )

    return json.loads(response.text)


def generate_code_explanation(code):

    start_time = time.time()

    print("🚀 Sending code to Gemini...")

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=f"""
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
    )

    elapsed = time.time() - start_time

    print(
        f"🤖 Gemini code explanation took: {elapsed:.2f} seconds"
    )

    return response.text