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

    path('coding/', views.CodingListCreateView.as_view()),
    path('coding/<int:pk>/', views.CodingDetailView.as_view()),

    path('testCases/', views.TestCaseListCreateView.as_view()),
    path('testCases/<int:pk>/', views.TestCaseDetailView.as_view()),

    path('subjective/', views.SubjectListCreateView.as_view()),
    path('subjective/<int:pk>/', views.SubjectiveDetailView.as_view()),

    path('testRegistration/<int:testid>/', views.RegisterUserTest.as_view()),

    path('getMcqQuestion/<int:testid>/', views.GetMcqQuestions.as_view()),
    path('submitMcq/<int:testid>/', views.SubmitMcq.as_view()),

    path('getSubjectiveQuestions/<int:testid>/', views.GetSubjectiveQuestions.as_view()),
    path('submitSubjective/<int:testid>/', views.SubmitSubjective.as_view()),

    path('getCodingQuestions/<int:testid>/', views.GetCodingQuestions.as_view()),
    path('submitCoding/<int:testid>/', views.CodingSubmissionView.as_view()),

    path('generalDashboard', views.getAllTests.as_view()),

    path('SusImages/<int:testid>/', views.UploadSusImages.as_view()),
    path('SusScore/<int:testid>/<int:userid>/', views.UpdateSusScore.as_view()),

    path('getRegisteredUsers/<int:testid>/', views.getRegisteredUserForTest.as_view()),

    path('getMcqScore/<int:testid>/<int:userid>/', views.getMcqScore.as_view()),
]
