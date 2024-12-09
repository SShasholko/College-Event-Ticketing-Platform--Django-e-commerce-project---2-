from django.db import models
from django.conf import settings
from events.models import Event 
import qrcode
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from cloudinary.uploader import upload
from cloudinary.models import CloudinaryField

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)  # Number of tickets purchased
    stripe_payment_intent_id = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    qr_code = CloudinaryField('QR Code', blank=True)

    def __str__(self):
        return f'Payment {self.id} - {self.amount} by {self.user}'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.qr_code:
            self.generate_qr_code()

    def generate_qr_code(self):
        """Generates a QR code containing event details and ticket information, uploads it to Cloudinary, and updates the qr_code field."""
        qr_data = f"Event: {self.event.title}, Date: {self.event.date_time}, Ticket ID: {self.id}, User: {self.user}"
        qr = qrcode.make(qr_data)


        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        buffer.seek(0)


        file_to_upload = SimpleUploadedFile(f"qr_code_{self.id}.png", buffer.read(), content_type='image/png')


        upload_result = upload(file_to_upload, folder="payments/qr_codes/")


        self.qr_code = upload_result['url']
        self.save(update_fields=['qr_code'])

