from django.contrib import admin
from .models import Payment

# Register your models here.
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'event', 'amount', 'quantity', 'status', 'created_at')
    search_fields = ('user__username', 'event__title', 'stripe_payment_intent_id')
    list_filter = ('status', 'created_at')