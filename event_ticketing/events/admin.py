from django.contrib import admin
from .models import Event

# Register your models here.
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_time', 'venue', 'ticket_price')
    # Display the image in the admin (optional)
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        return obj.image and f'<img src="{obj.image.url}" width="100" />'
    image_preview.allow_tags = True
    image_preview.short_description = 'Image Preview'

admin.site.register(Event, EventAdmin)