"""
URL configuration for jobboard project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from jobs import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('register/seeker/', views.register_seeker, name='register_seeker'),
    path('register/poster/', views.register_poster, name='register_poster'),
    path('login/', auth_views.LoginView.as_view(
        template_name='jobs/login.html',
        extra_context={'next': '/'}
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    # Job URLs
    path('jobs/post/', views.post_job, name='post_job'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('my-jobs/', views.my_jobs, name='my_jobs'),
    
    # Category URLs
    path('jobs/category/<int:category_id>/', views.jobs_by_category, name='jobs_by_category'),
    
    path('applications/<int:application_id>/update/', views.update_application, name='update_application'),
    path('jobs/<int:job_id>/applications/', views.job_applications, name='job_applications'),
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('jobs/<int:job_id>/applications/', views.view_applications, name='view_applications'),
    path('dashboard/', views.job_seeker_dashboard, name='job_seeker_dashboard'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)