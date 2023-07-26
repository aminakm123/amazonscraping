from django.contrib import admin
from django.urls import path,include



urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include(('amazon_scrapper.urls','amazon_scrapper'),namespace='amazon_scrapper'))
]
