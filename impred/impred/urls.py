from django.urls import path

from . import views

app_name = 'impred'

urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.main, name='main'),
    path('loadimage/', views.loadimage, name='loadimage'),
    path('predictimage/', views.predictimage, name='predictimage'),
]
