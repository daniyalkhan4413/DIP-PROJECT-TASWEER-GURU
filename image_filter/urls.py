from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('process/', views.process_image_view, name='process_image'),
    path('lander/',views.landingpage, name = 'landingpage')

]