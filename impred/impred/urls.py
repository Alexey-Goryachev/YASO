from django.urls import path

from . import views

app_name = 'impred'

urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.main, name='main'),
    path('loadimage/', views.loadimage, name='loadimage'),
    path('predictimage/', views.predictimage, name='predictimage'),
    path('netmodels/', views.netmodels, name='netmodels'),
    path('netmodel/', views.netmodel, name='netmodel'),
    path('netmodel/<int:id>', views.netmodel, name='netmodel'),
    # path('labels/', views.labels, name='labels'),
    # path('label/<int:netmodel_id>', views.label, name='label'),
]
