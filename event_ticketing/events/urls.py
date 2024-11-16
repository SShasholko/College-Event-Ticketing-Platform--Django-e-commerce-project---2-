from django.urls import path, include
from . import views


urlpatterns = [
    path('<int:event_id>/', views.event_detail, name='event_detail'),
    path('<int:event_id>/purchase/', views.ticket_purchase, name='ticket_purchase'),
    path('', views.event_list, name='event_list'),
]
