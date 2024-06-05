from django.contrib import admin
from django.urls import path, include
from auto_manito import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('', include('users.urls')),
]
