from django.shortcuts import render, get_object_or_404, redirect
from .models import Event, Ticket, Category
from .forms import TicketPurchaseForm, EventForm
from datetime import datetime  
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from payments.models import Payment
from django.contrib.auth.decorators import login_required



def home(request):
    # Fetch the three soonest events
    current_time = timezone.now()
    soonest_events = Event.objects.filter(date_time__gte=current_time).order_by('date_time')[:3]

    context = {
        'soonest_events': soonest_events,
        'current_year': datetime.now().year,
    }
    
    return render(request, 'events/home.html', context)



# Create your views here.
def event_list(request):
    # Get the search query and category filter from the request
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', None)

    current_time = timezone.now()

    events = Event.objects.filter(date_time__gte=current_time).order_by('date_time')


     # If there is a search query, filter events by title (case-insensitive)
    if search_query:
        events = events.filter(title__icontains=search_query)

    
    if category_filter:
        events = events.filter(category_id=category_filter)
    
    # Get all categories for the dropdown menu
    categories = Category.objects.all()

    context = {
        'events': events,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
    }

    # return render(request, 'events/event_list.html', {'events': events})
    return render(request, 'events/event_list.html', context)

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/event_detail.html', {'event': event})


def ticket_purchase(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = TicketPurchaseForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.event = event  # Assign the event to the ticket
            ticket.save()
            return redirect('event_detail', event_id=event.id)  # Redirect to the event detail page after purchase
    else:
        form = TicketPurchaseForm(initial={'event': event})

    quantity = form.data.get('quantity', 1)  # Get the quantity from the form data
    quantity = int(quantity) if quantity else 1
    total_price = quantity * event.ticket_price  # Calculate the total price

    return render(request, 'events/ticket_purchase.html', {'form': form, 'event': event, 'price': event.ticket_price, 'total_price': total_price, 'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY})


@login_required
def profile_view(request):
    # Retrieve events created by the user
    created_events = Event.objects.filter(user=request.user)
    
    # Retrieve events the user has purchased tickets for
    purchased_payments = Payment.objects.filter(user=request.user)
    purchased_events = [payment.event for payment in purchased_payments]  # Extract events from payments

    # Pass both created and purchased events to the template
    context = {
        'created_events': created_events,
        'purchased_events': purchased_events,
        'purchased_payments': purchased_payments,
    }
    return render(request, 'events/profile.html', context)


def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user  # Assign the event to the logged-in user
            event.save()
            return redirect('profile')  # Redirect to profile page after event creation
    else:
        form = EventForm()

    return render(request, 'events/add_event.html', {'form': form})


def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, user=request.user)  # Ensure the user can only edit their events
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the profile page
    else:
        form = EventForm(instance=event)
    return render(request, 'events/edit_event.html', {'form': form})


def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, user=request.user)
    if request.method == 'POST':
        event.delete()
        messages.success(request, "Event deleted successfully!")
        return redirect('profile')  # Redirect to the profile page
    return render(request, 'events/delete_event.html', {'event': event})




