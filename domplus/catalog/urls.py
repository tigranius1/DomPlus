from django.urls import path
from . import views

urlpatterns = [
    path('', views.catalog, name='catalog'),
    path('apartment/<int:pk>/', views.apartment_detail, name='apartment_detail'),
    path('favorite/<int:pk>/toggle/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorites_list, name='favorites_list'),
    path('request/<int:pk>/', views.submit_request, name='submit_request'),
]