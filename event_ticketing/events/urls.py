from django.urls import path
from . import views

urlpatterns = [
    # Define the URL for the event detail page
    path('<int:event_id>/', views.event_detail, name='event_detail'),


   # path('events/', views.event_list, name='event_list'),
    path('', views.event_list, name='event_list'),

]
