from django.contrib import admin
from django.urls import path
from detection import views  # Import your views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('upload/', views.upload_file, name='upload'),
    path('plagiarism-check/', views.plagiarism_check, name='plagiarism_check'),
]
