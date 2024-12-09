from django.shortcuts import render, get_object_or_404, redirect
from .models import Event, Ticket, Category
from .forms import TicketPurchaseForm, EventForm
from datetime import datetime  
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from payments.models import Payment
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib.auth import logout
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import random
import string
import os


def home(request):
    """Renders the 'home.html' template with the 6 soonest upcoming events and the current year."""
    current_time = timezone.now()
    soonest_events = Event.objects.filter(date_time__gte=current_time).order_by('date_time')[:6]

    context = {
        'soonest_events': soonest_events,
        'current_year': datetime.now().year,
    }
    
    return render(request, 'events/home.html', context)


def event_list(request):
    """Displays a list of upcoming events filtered by search query and category, and provides all categories for user selection in the template."""
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', None)
    current_time = timezone.now()
    events = Event.objects.filter(date_time__gte=current_time).order_by('date_time')

    if search_query:
        events = events.filter(title__icontains=search_query)

    if category_filter:
        events = events.filter(category_id=category_filter)
    
    categories = Category.objects.all()

    context = {
        'events': events,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
    }

    return render(request, 'events/event_list.html', context)


def event_detail(request, event_id):
    """Fetches event details by ID, calculates tickets sold and remaining tickets, and renders the 'event_detail.html' template with this information."""
    event = get_object_or_404(Event, id=event_id)

    tickets_sold = event.payments.aggregate(total_sold=Sum('quantity'))['total_sold'] or 0
    remaining_tickets = event.total_tickets - tickets_sold

    context = {
        'event': event,
        'tickets_sold': tickets_sold,
        'remaining_tickets': remaining_tickets,
    }

    return render(request, 'events/event_detail.html', context)


@login_required
def ticket_purchase(request, event_id):
    """Handles ticket purchase for a specific event, processes form submission, calculates the total price, and renders the 'ticket_purchase.html' template with the event details and Stripe public key."""
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = TicketPurchaseForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.event = event  
            ticket.save()
            return redirect('event_detail', event_id=event.id)
    else:
        form = TicketPurchaseForm(initial={'event': event})

    quantity = form.data.get('quantity', 1)
    quantity = int(quantity) if quantity else 1
    total_price = quantity * event.ticket_price

    return render(request, 'events/ticket_purchase.html', {'form': form, 'event': event, 'price': event.ticket_price, 'total_price': total_price, 'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY})


@login_required
def profile_view(request):
    """Displays the user profile with their created events (upcoming and past, including ticket sales) and a list of events they have purchased tickets for, rendering the 'profile.html' template with this data."""
    created_events = Event.objects.filter(user=request.user)
    upcoming_events = created_events.filter(date_time__gte=timezone.now()).order_by('date_time')
    past_events = created_events.filter(date_time__lt=timezone.now()).order_by('-date_time')
    upcoming_events = upcoming_events.annotate(tickets_sold=Sum('payments__quantity'))
    past_events = past_events.annotate(tickets_sold=Sum('payments__quantity'))
    purchased_payments = Payment.objects.filter(user=request.user)
    purchased_events = [payment.event for payment in purchased_payments]  

    context = {
        'created_events': created_events,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'purchased_events': purchased_events,
        'purchased_payments': purchased_payments,
    }
    return render(request, 'events/profile.html', context)

  #
        
def add_event(request):
    """Handles the creation of a new event, processes the submitted form, saves the event with the current user as the creator, and renders the 'add_event.html' template for form input."""
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            #photo = random_name+os.path.splitext(str(request.FILES["image"]))[1]
            #upload_result = cloudinary.uploader.upload(request.FILES["image"], public_id=photo)
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            messages.success(request, "Your event has been successfully added!")
            return redirect('profile')
    else:
        form = EventForm()

    return render(request, 'events/add_event.html', {'form': form})


def edit_event(request, event_id):
    """"Allows the event creator to edit an existing event, updates the event details upon form submission, and renders the 'edit_event.html' template with the event form."""
    event = get_object_or_404(Event, id=event_id, user=request.user)  
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():

            form.save()
            messages.success(request, f'The event "{event.title}" was successfully updated.')
            return redirect('profile')
    else:
        form = EventForm(instance=event)
    return render(request, 'events/edit_event.html', {'form': form})


def delete_event(request, event_id):
    """Handles the deletion of an event by its creator, removes the event upon form submission, and renders the 'delete_event.html' template for confirmation."""
    event = get_object_or_404(Event, id=event_id, user=request.user)

    if request.method == 'POST':
        event.delete()
        messages.success(request, f'The event "{event.title}" was successfully deleted.')
        return redirect('profile')

    return render(request, 'events/delete_event.html', {'event': event})



def logout_view(request):
    """Renders the 'logout.html' template to display a logout confirmation page."""
    return render(request, 'account/logout.html')


def logout_confirm(request):
    """Logs out the user upon form submission, shows a success message, and redirects to the homepage."""
    if request.method == 'POST':
        logout(request)
        messages.success(request, "You have successfully logged out.")
        return redirect('home')


