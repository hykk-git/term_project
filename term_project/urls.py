from django.contrib import admin
from django.urls import path
from auto_manito import views
from auto_manito.views import CustomLoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('assign/', views.assign_manito, name='assign_manito'),
    path('check/', views.check_manito, name='check_manito'),
    path('register/group/', views.register_group, name='register_group'),
    path('register/user/', views.register_user, name='register_user'),
    path('success/', views.success, name='success'),
    path('get_users/<int:group_id>/', views.get_users, name='get_users'),
    path('manito_message/', views.manito_message, name='manito_message'),
]
