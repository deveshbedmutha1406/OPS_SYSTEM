from django.urls import path, include
from . import views

urlpatterns = [
    path('register/', views.UserRegistration.as_view()),
    path('login/', views.LoginUser.as_view()),
    path('logout/', views.LogoutUser.as_view()),

]
