from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name



class Event(models.Model):
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


class Ticket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    purchaser_name = models.CharField(max_length=100)
    email = models.EmailField()
    quantity = models.PositiveIntegerField()
    purchased_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
