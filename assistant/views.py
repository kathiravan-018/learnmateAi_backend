from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import RegisterSerializer
from .services import (
    generate_ai_response,
    generate_notes,
    generate_quiz,
    generate_code_explanation,
)


# ============================================================
# HEALTH CHECK
# ============================================================

@api_view(["GET"])
def home(request):

    return Response({
        "status": "success",
        "message": "LearnMate AI backend is running"
    })


# ============================================================
# AI CHAT
# ============================================================

@api_view(["POST"])
def chat(request):

    message = request.data.get("message")
    history = request.data.get("history", [])

    if not message:
        return Response(
            {"error": "Message is required."},
            status=400
        )

    if not isinstance(history, list):
        history = []

    try:

        response = generate_ai_response(
            message,
            history
        )

        return Response({
            "response": response
        })

    except Exception as e:

        print("❌ Chat / Gemini Error:", str(e))

        return Response(
            {
                "error": (
                    "AI service is temporarily unavailable. "
                    "Please try again."
                )
            },
            status=503
        )


# ============================================================
# NOTES
# ============================================================

@api_view(["POST"])
def notes(request):

    topic = request.data.get("topic")

    if not topic:
        return Response(
            {"error": "Topic is required."},
            status=400
        )

    try:

        notes_response = generate_notes(topic)

        return Response({
            "response": notes_response
        })

    except Exception as e:

        print("❌ Notes / Gemini Error:", str(e))

        return Response(
            {
                "error": (
                    "Unable to generate notes right now. "
                    "Please try again."
                )
            },
            status=503
        )
# ============================================================
# QUIZ
# ============================================================

@api_view(["POST"])
def quiz(request):

    topic = request.data.get("topic")

    previous_questions = request.data.get(
        "previous_questions",
        []
    )

    if not topic:
        return Response(
            {"error": "Topic is required."},
            status=400
        )

    if not isinstance(previous_questions, list):
        previous_questions = []

    try:

        quiz_response = generate_quiz(
            topic,
            previous_questions
        )

        return Response({
            "quiz": quiz_response
        })

    except Exception as e:

        print("❌ Quiz / Gemini Error:", str(e))

        return Response(
            {
                "error": (
                    "Unable to generate quiz right now. "
                    "Please try again."
                )
            },
            status=503
        )


# ============================================================
# CODE EXPLANATION
# ============================================================

@api_view(["POST"])
def code_explain(request):

    code = request.data.get("code")

    if not code:
        return Response(
            {"error": "Code is required."},
            status=400
        )

    try:

        explanation = generate_code_explanation(code)

        return Response({
            "explanation": explanation
        })

    except Exception as e:

        print(
            "❌ Code Explanation / Gemini Error:",
            str(e)
        )

        return Response(
            {
                "error": (
                    "Unable to explain the code right now. "
                    "Please try again."
                )
            },
            status=503
        )


# ============================================================
# REGISTER
# ============================================================

class RegisterView(generics.CreateAPIView):

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


# ============================================================
# CURRENT USER
# ============================================================

class CurrentUserView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
        })