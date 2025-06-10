
from django.contrib import admin
from django.urls import path, include
from django.views.csrf import csrf_failure

handler403 = csrf_failure


urlpatterns = [
    path('', include('reports.urls', namespace='reports')),
    path('admin/',   admin.site.urls),
]