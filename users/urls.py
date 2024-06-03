from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    path('login/', login, name='login'),
    path('manito_message/', manito_message, name='manito_message'),
    path('get_users/<int:group_id>/', get_users, name='get_users'),
    path('register/group/', register_group, name='register_group'),
    path('register/user/', register_user, name='register_user'),
    path('success/', success, name='success'),
]
