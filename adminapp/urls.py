from django.urls import path
from .views import *

urlpatterns = [
    path('manager_login/', manager_login, name='manager_login'),
    path('manager_dashboard/', manager_dashboard, name='manager_dashboard'),
    path('delete_announcement/<int:announcement_id>/', delete_announcement, name='delete_announcement'),
    path('delete_group/', delete_group, name='delete_group'),
]
