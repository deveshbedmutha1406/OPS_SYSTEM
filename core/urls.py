from django.urls import path, include
from . import views

urlpatterns = [
    path('register/', views.UserRegistration.as_view()),
    path('login/', views.LoginUser.as_view()),
    path('logout/', views.LogoutUser.as_view()),

    path('test/', views.TestListCreateView.as_view()),
    path('test/<int:testid>', views.TestDetailView.as_view()),

    path('getSection/<int:testid>', views.SectionListView.as_view()),
    path('createSection/', views.SectionCreateView.as_view()),
    path('removeSection/<int:sid>', views.SectionDestroyView.as_view()),

    path('mcq/', views.McqListCreateView.as_view()),
    path('mcq/<int:pk>/', views.McqDetailView.as_view()),

    path('subjective/', views.SubjectListCreateView.as_view()),
    path('subjective/<int:pk>/', views.SubjectiveDetailView.as_view()),

    path('testRegistration/<int:testid>/', views.RegisterUserTest.as_view()),

    path('getMcqQuestion/<int:testid>/', views.GetMcqQuestions.as_view()),
]
