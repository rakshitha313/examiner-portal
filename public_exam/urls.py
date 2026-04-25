from django.urls import path
from django.shortcuts import redirect
from . import views

def home_redirect(request):
    return redirect('/examiner/signup/')

urlpatterns = [
    path('', home_redirect, name='home'),
    path('dashboard/', views.examiner_dashboard, name='examiner-dashboard'),
    path('create-exam/', views.create_exam, name='create-exam'),
    path('edit-exam/<int:pk>/', views.edit_exam, name='edit-exam'),
    path('delete-exam/<int:pk>/', views.delete_exam, name='delete-exam'),
    path('add-question/<int:pk>/', views.add_question, name='add-question'),
    path('delete-question/<int:pk>/', views.delete_question, name='delete-question'),
    path('edit-question/<int:pk>/', views.edit_question, name='edit-question'),
    path('publish-exam/<int:pk>/', views.publish_exam, name='publish-exam'),
    path('exam/<str:exam_code>/', views.public_exam_entry_view, name='public-exam-entry'),
    path('exam/<str:exam_code>/start/', views.public_exam_start_view, name='public-exam-start'),
    path('exam/<str:exam_code>/submit/', views.submit_public_exam, name='submit-public-exam'),
    path('exam/<str:exam_code>/result/', views.public_exam_result_view, name='public-exam-result'),
    path('results/', views.examiner_results_view, name='examiner-results'),
]