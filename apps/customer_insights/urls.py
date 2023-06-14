from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'customer_insights'
urlpatterns = [
    path('', views.main, name='main'),
    path('fetch_new_asin_data', views.fetch_new_asin_data, name='fetch_new_asin_data'),
    path('customer_reviews', views.customer_reviews, name='customer_reviews'),
    path('product_groups', views.product_groups, name='product_groups'),
    path('update_user_product_categories', views.update_user_product_categories, name='update_user_product_categories'),
    path('delete_user_product_group', views.delete_user_product_group, name='delete_user_product_group'),
    path('beta_tester_signup', views.beta_tester_signup, name='beta_tester_signup'),
]