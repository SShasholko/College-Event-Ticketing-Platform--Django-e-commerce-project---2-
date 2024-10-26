from django.urls import path
from . import views

urlpatterns = [
    path('checkout/<int:event_id>/', views.create_checkout_session, name='checkout'),  
    path('webhook/', views.stripe_webhook, name='stripe-webhook'),


    path('success/', views.success_view, name='success'),
    path('cancel/', views.cancel_view, name='cancel'),
]