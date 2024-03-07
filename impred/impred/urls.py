from django.urls import path

from . import views

app_name = 'impred'

urlpatterns = [
    path('', views.main, name='main'),
    path('loadimage/', views.loadimage, name='loadimage'),
    path('predictimages/', views.predictimages, name='predictimages'),
    path('predictimage/<int:id>', views.predictimage, name='predictimage'),
    path('predictimage/<int:id>/delete', views.predictimage_del, name='predictimage_del'),
    path('predictimage/<int:image_id>/retrain', views.retrainmodel, name='predictimage_retrain'),
    path('predictimage/', views.predictimage, name='predictimage'),
    path('netmodels/', views.netmodels, name='netmodels'),
    path('netmodel/', views.netmodel, name='netmodel'),
    path('netmodel/<int:id>', views.netmodel, name='netmodel'),
]
