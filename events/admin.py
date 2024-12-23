from django.contrib import admin
from .models import Category, Event, Ticket

# Register your models here.
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_time', 'venue', 'ticket_price')
    # Display the image in the admin
    readonly_fields = ('image_preview',)
    def image_preview(self, obj):
        return obj.image and f'<img src="{obj.image.url}" width="100" />'
    image_preview.allow_tags = True
    image_preview.short_description = 'Image Preview'

admin.site.register(Event, EventAdmin)
admin.site.register(Category)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('event', 'purchaser_name', 'email', 'quantity', 'purchased_at')
    search_fields = ('purchaser_name', 'email')