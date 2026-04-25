from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.examiner_signup_view, name='examiner-signup'),
    path('login/', views.examiner_login_view, name='examiner-login'),
    path('logout/', views.examiner_logout_view, name='examiner-logout'),
    
]