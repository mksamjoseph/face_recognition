"""
URL configuration for pro1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from app.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home', home, name='home'),
    path('camera2/', camera2_view, name='camera2'),
    path('admin/', admin.site.urls),
    path('', landingpage, name='landingpage'),
    path('login/', login_view, name='login'),
    path('dash/', dashboarad, name='dash'),
    path('feature/', feature, name='feature'),
    path('team/', team, name='team'),
    path('camera/', camera, name='camera'),
    path('livefeed/', live_feed, name='live_feed'),
    path('logout/', logout_user, name='logout'),
    path('api/logs/', get_initial_logs, name='get_initial_logs'),
    path('api/stats/', get_stats, name='get_stats'),
    path('get-stats/', get_stat, name='get_stat'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
