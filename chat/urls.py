from django.urls import path 
from . import views 
from .views import signup, login


urlpatterns = [
    path('', views.lobby),
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
]