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
from django.db import transaction 
import requests

stripe.api_key = settings.STRIPE_SECRET_KEY


@require_POST
@login_required
def create_payment_intent(request, event_id):
    """Creates a Stripe PaymentIntent for ticket purchase, verifies quantity and ticket availability, updates the remaining tickets, and records the payment while handling errors and sending a confirmation email."""
    event = get_object_or_404(Event, id=event_id)

    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
        if quantity <= 0:
            return JsonResponse({'error': 'Quantity must be at least 1'}, status=400)

        if event.remaining_tickets < quantity:
            return JsonResponse({'error': 'Not enough tickets available'}, status=400)

        amount = int(event.ticket_price * quantity * 100)

        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="gbp",
            metadata={"event_id": event.id, "user_id": request.user.id},
        )

        with transaction.atomic():
            event.remaining_tickets -= quantity
            event.save()

            payment = Payment.objects.create(
                user=request.user,
                event=event,
                amount=amount / 100,
                quantity=quantity,
                stripe_payment_intent_id=intent.id
            )
            send_ticket_email(payment, event)

        return JsonResponse({
            "client_secret": intent.client_secret,
            "updated_remaining_tickets": event.remaining_tickets
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def send_ticket_email(payment, event):
    """Send an email with ticket details and QR code after successful payment."""
    subject = f"Your Ticket for {event.title}"
    recipient_email = getattr(payment.user, 'email', None)  

    if not recipient_email:
        print(f"ERROR: No email address found for user {payment.user}")
        return  

    context = {
        'user': payment.user,
        'event': event,
        'quantity': payment.quantity,
        'amount': payment.amount,
    }

    try:
        # Render email content
        message = render_to_string('payments/ticket_email.html', context)
        email = EmailMessage(subject, message, to=[recipient_email])
        email.content_subtype = 'html'

        # Attach QR code from Cloudinary if it exists
        if payment.qr_code:
            qr_code_url = payment.qr_code  # Cloudinary URL
            response = requests.get(qr_code_url, stream=True)

            if response.status_code == 200:
                email.attach(f"qr_code_{payment.id}.png", response.content, 'image/png')
                print(f"INFO: Attached QR code for payment {payment.id}")
            else:
                print(f"WARNING: Failed to download QR code from {qr_code_url} for payment {payment.id}")
        else:
            print(f"WARNING: No QR code found for payment {payment.id}")

        # Send the email
        email.send()
        print(f"INFO: Email sent to {recipient_email} for event {event.title}")

    except Exception as e:
        print(f"ERROR: Failed to send email for payment {payment.id}: {e}")



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
