from django.urls import path
from .views import RegisterView
from .views import chat, notes, quiz, code_explain, CurrentUserView


urlpatterns = [

    path("chat/", chat),

    path("notes/", notes),

    path("quiz/", quiz),

     path("code-explain/", code_explain),

      path(
        "register/",
        RegisterView.as_view(),
        name="register",

    ),
    path(
        "me/",
        CurrentUserView.as_view(),
        name="current-user",
    ),

]