from django.shortcuts import render, get_object_or_404, redirect
from .models import Event, Ticket, Category
from .forms import TicketPurchaseForm

# Create your views here.
def event_list(request):
    # Get the search query and category filter from the request
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', None)

    events = Event.objects.all().order_by('date_time')
    # events = Event.objects.all()

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



    return render(request, 'events/ticket_purchase.html', {'form': form, 'event': event, 'price': event.ticket_price, 'total_price': total_price})