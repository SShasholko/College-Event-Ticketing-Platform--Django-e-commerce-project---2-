from django.db import models
from django.contrib.auth.models import User 

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name



class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_time = models.DateTimeField()
    venue = models.CharField(max_length=255)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_tickets = models.IntegerField()
    remaining_tickets = models.IntegerField()
    image = models.ImageField(upload_to='event_images/', null=True, blank=True)

    #    Link to category
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)  

    def save(self, *args, **kwargs):
        # When creating a new event, set remaining_tickets to total_tickets
        if not self.pk:  # Only set this when the event is first created
            self.remaining_tickets = self.total_tickets
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Ticket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    purchaser_name = models.CharField(max_length=100)
    email = models.EmailField()
    quantity = models.PositiveIntegerField()
    purchased_at = models.DateTimeField(auto_now_add=True)

def __str__(self):
    return f"{self.purchaser_name} - {self.event.title} - {self.quantity} tickets"

