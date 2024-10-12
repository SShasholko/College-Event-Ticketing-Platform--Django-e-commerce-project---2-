from django.urls import path, include
from . import views

urlpatterns = [
    # Define the URL for the event detail page
    path('<int:event_id>/', views.event_detail, name='event_detail'),

    path('<int:event_id>/purchase/', views.ticket_purchase, name='ticket_purchase'),
    
   # path('events/', views.event_list, name='event_list'),
    path('', views.event_list, name='event_list'),
]
