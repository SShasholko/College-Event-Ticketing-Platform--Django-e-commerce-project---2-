from django.shortcuts import render

# Create your views here.

import stripe
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect,  get_object_or_404
from payments.models import Payment
from events.models import Event 
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging
from django.core.mail import EmailMessage




stripe.api_key = settings.STRIPE_SECRET_KEY

@require_POST
@login_required
def create_checkout_session(request, event_id):
    """Create a Stripe Checkout Session for purchasing an event ticket."""
    event = get_object_or_404(Event, id=event_id)

    try:
        # Get quantity from the request data
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))  # Default to 1 if not provided
        if quantity <= 0:
            return JsonResponse({'error': 'Quantity must be at least 1'}, status=400)

        amount = int(event.ticket_price * quantity * 100)  # Convert total amount to cents

        # Create a Stripe Checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': event.title,
                    },
                    'unit_amount': int(event.ticket_price * 100),
                },
                'quantity': quantity,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/payments/success/'),
            cancel_url=request.build_absolute_uri('/payments/cancel/'),
        )

        # Save payment information with session.id as stripe_payment_intent_id
        payment = Payment.objects.create(
            user=request.user,
            event=event,
            amount=amount / 100,  # Save amount in dollars
            quantity=quantity,
            stripe_payment_intent_id=session.id  # Using session.id here
        )

        send_ticket_email(payment, event)

        return JsonResponse({'id': session.id})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def send_ticket_email(payment, event):
    """Send an email with ticket details and QR code after successful payment."""
    subject = f"Your Ticket for {event.title}"
    recipient_email = payment.user.email
    context = {
        'user': payment.user,
        'event': event,
        'quantity': payment.quantity,
        'amount': payment.amount,
    }
    
    try:
        # Render the email body
        message = render_to_string('payments/ticket_email.html', context)

        # Create the email object
        email = EmailMessage(subject, message, to=[recipient_email])
        email.content_subtype = 'html'  # Send as HTML email

        # Attach the QR code
        if payment.qr_code and payment.qr_code.path:
            email.attach_file(payment.qr_code.path)
            logging.info(f"Attached QR code for payment {payment.id}")
        else:
            logging.warning(f"No QR code found for payment {payment.id}")

        # Send the email
        email.send()
        logging.info(f"Email sent to {recipient_email} for event {event.title}")

    except Exception as e:
        logging.error(f"Failed to send email for payment {payment.id}: {e}")


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
