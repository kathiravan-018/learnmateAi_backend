from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer
from .services import generate_ai_response,generate_notes,generate_quiz,generate_code_explanation


@api_view(["POST"])
def chat(request):

    message = request.data.get("message")
    history = request.data.get("history", [])

    response = generate_ai_response(message,history)

    return Response({
        "response": response
    })

@api_view(["POST"])
def notes(request):

    topic = request.data.get("topic")

    if not topic:
        return Response(
            {"error" : "Topic is required ."},
            status=400
        )
    notes = generate_notes(topic)

    return Response({
        "response": notes
    })

@api_view(["POST"])
def quiz(request):

    topic = request.data.get("topic")
    previous_questions = request.data.get(
        "previous_questions",
        []
    )

    response = generate_quiz(
        topic,
        previous_questions
    )

    return Response({
        "quiz": response
    })

@api_view(["POST"])
def code_explain(request):

    code = request.data.get("code")

    if not code:
        return Response(
            {"error": "Code is required."},
            status=400
        )

    explanation = generate_code_explanation(code)

    return Response({
        "explanation": explanation
    })


class RegisterView(generics.CreateAPIView):

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
        })