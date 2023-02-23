from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'amazon'
urlpatterns = [
    path('', views.main, name='main'),
]