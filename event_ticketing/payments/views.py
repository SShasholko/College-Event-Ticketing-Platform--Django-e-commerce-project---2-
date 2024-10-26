from django.shortcuts import render

# Create your views here.

import stripe
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect,  get_object_or_404
from .models import Payment
from events.models import Event 
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


stripe.api_key = settings.STRIPE_SECRET_KEY

@require_POST
@login_required
def create_checkout_session(request, event_id):
    """Create a Stripe Checkout Session for purchasing an event ticket."""
    if not request.user.is_authenticated:
        return redirect(f"{settings.LOGIN_URL}?next=/payments/checkout/{event_id}/")
    
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        # Get quantity from the request data
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))  # Default to 1 if not provided
        if quantity <= 0:
            return JsonResponse({'error': 'Quantity must be at least 1'}, status=400)

        amount = int(event.ticket_price*100)  # Convert to cents

        # Create a Stripe Checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': event.title,
                    },
                    'unit_amount': amount,
                },
                'quantity': quantity,  # Adjust this based on user input
            }],
            mode='payment',
            success_url='https://d830-2a02-c7c-1605-600-fcb5-eb3d-592d-2983.ngrok-free.app/payments/success/',
            cancel_url='https://d830-2a02-c7c-1605-600-fcb5-eb3d-592d-2983.ngrok-free.app/payments/cancel/',
        )

        return JsonResponse({'id': session.id})
    return JsonResponse({'error': 'Invalid request'}, status=400)




@csrf_exempt
def stripe_webhook(request):
    """Stripe webhook to confirm the payment."""
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET 
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
    
        payment = Payment.objects.get(stripe_payment_intent_id=intent['id'])
        payment.status = 'succeeded'
        payment.save()

    return JsonResponse({'status': 'success'})


def success_view(request):
    """View for successful payment."""
    return render(request, 'payments/success.html')

def cancel_view(request):
    """View for canceled payment."""
    return render(request, 'payments/cancel.html')
