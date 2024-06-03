from django.contrib import admin
from django.urls import path, include
from auto_manito import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('get_users/<int:group_id>/', views.get_users, name='get_users'),
    path('manito_message/', views.manito_message, name='manito_message'),
    path('users/', include('users.urls')),
]
