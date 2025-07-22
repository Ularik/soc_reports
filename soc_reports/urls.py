from ninja import NinjaAPI
from user.api import router as user_router

api = NinjaAPI()

api.add_router("/events/", user_router)


from django.contrib import admin
from django.urls import path, include
from django.views.csrf import csrf_failure

handler403 = csrf_failure

urlpatterns = [
    path('', include('reports.urls', namespace='reports')),
    path('api/', api.urls, name='api'),

    path('user/', include('user.urls')),
    path('admin/',   admin.site.urls),
]