from django import forms
from .models import Ticket, Event
from django.forms.widgets import DateTimeInput

class TicketPurchaseForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, initial=1)  # Add quantity field
    class Meta:
        model = Ticket
        fields = ['event', 'purchaser_name', 'email', 'quantity']
        widgets = {
            'event': forms.HiddenInput(),
        }
    def total_price(self, event_price):
        return self.cleaned_data['quantity'] * ticket_price  # Calculate total price

class EventForm(forms.ModelForm):
    date_time = forms.DateTimeField(
        widget=DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        label='Event Date and Time'
    )
    class Meta:
        model = Event
        fields = ['title', 'description', 'date_time', 'venue', 'ticket_price', 'total_tickets', 'category', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter event title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter event description'}),
            'venue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter event venue'}),
            'ticket_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter ticket price'}),
            'total_tickets': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter total tickets'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }