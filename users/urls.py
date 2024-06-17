from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    path('login/', user_login, name='user_login'),
    path('manito_message/', manito_message, name='manito_message'),
    path('get_users/', get_users, name='get_users'),
    path('register/group/', register_group, name='register_group'),
    path('register/user/', register_user, name='register_user'),
    path('success/', success, name='success'),
    path('send_message/', send_message, name='send_message'),
    path('inbox/', inbox, name='inbox'),
    path('delete_message/<int:message_id>/', delete_message, name='delete_message'),
    path('logout/', logout_view, name='logout_view'),
]
