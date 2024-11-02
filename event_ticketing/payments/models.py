from django.db import models
from django.conf import settings
from events.models import Event  # Import Event to create a relationship
import qrcode
from io import BytesIO
from django.core.files import File

# Create your models here.

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)  # Number of tickets purchased
    stripe_payment_intent_id = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)

    def __str__(self):
        return f'Payment {self.id} - {self.amount} by {self.user}'
    
    def save(self, *args, **kwargs):
        # Save the instance first to ensure it has an ID
        super().save(*args, **kwargs)
        
        # Only generate QR code if it does not already exist
        if not self.qr_code:
            self.generate_qr_code()


    def generate_qr_code(self):
        # QR code data: adjust as needed
        qr_data = f"Event: {self.event.title}, Date: {self.event.date_time}, Ticket ID: {self.id}, User: {self.user}"
        qr = qrcode.make(qr_data)

        # Save QR code to BytesIO buffer
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        buffer.seek(0)

        # Save to qr_code field
        filename = f'qr_code_{self.id}.png'
        self.qr_code.save(filename, File(buffer), save=False)
        super().save(update_fields=['qr_code'])
        # Confirm file has been saved

