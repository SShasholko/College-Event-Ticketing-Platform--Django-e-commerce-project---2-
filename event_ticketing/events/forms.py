from django import forms
from .models import Ticket

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