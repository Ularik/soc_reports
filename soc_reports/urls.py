
from django.contrib import admin
from django.urls import path, include



urlpatterns = [
    path('', include('reports.urls', namespace='reports')),
    path('admin/',   admin.site.urls),
]