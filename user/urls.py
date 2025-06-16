from . import views
from django.urls import path

app_name = 'user'

urlpatterns = [
    path('login/', views.user_login_view, name='login'),
    path('logout/', views.user_logout_view, name='logout'),
]