from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'customer_insights'
urlpatterns = [
    path('', views.main, name='main'),
    path('fetch_new_asin_data', views.fetch_new_asin_data, name='fetch_new_asin_data'),
]