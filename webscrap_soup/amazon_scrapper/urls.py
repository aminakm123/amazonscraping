from django.urls import path,include
from amazon_scrapper import views


urlpatterns = [
    path('', views.scrape_and_export, name='scrape_and_export')
]
