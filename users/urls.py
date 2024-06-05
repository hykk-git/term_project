from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    path('login/', user_login, name='login'),
    path('manito_message/', manito_message, name='manito_message'),
    path('get_users/', get_users, name='get_users'),
    path('register/group/', register_group, name='register_group'),
    path('register/user/', register_user, name='register_user'),
    path('success/', success, name='success'),
    path('logout/', logout_view, name='logout'),
]
