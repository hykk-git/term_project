from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from auto_manito import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('', include('users.urls')),
    path('', include('adminapp.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
