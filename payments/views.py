import razorpay

from django.conf import settings
from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST

from bookings.models import Booking
from .models import Payment


@login_required
def create_payment(request, booking_id):

    # User can only pay for their own booking
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )


    # Prevent payment for cancelled bookings
    if booking.status == 'cancelled':

        messages.error(
            request,
            "Cancelled bookings cannot be paid for."
        )

        return redirect(
            'booking_detail',
            booking_id=booking.id
        )


    # Get existing payment if available
    payment = Payment.objects.filter(
        booking=booking
    ).first()


    # Prevent duplicate successful payment
    if payment and payment.status == 'success':

        messages.info(
            request,
            "This booking has already been paid for."
        )

        return redirect(
            'booking_detail',
            booking_id=booking.id
        )


    # Amount must be in paise
    amount_in_paise = int(
        booking.total_price * 100
    )


    # Create Razorpay client
    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )


    # Create Razorpay order
    razorpay_order = client.order.create(
        {
            'amount': amount_in_paise,
            'currency': 'INR',
            'payment_capture': 1
        }
    )


    # Create payment record if it doesn't exist
    if not payment:

        payment = Payment.objects.create(
            booking=booking,
            amount=booking.total_price,
            razorpay_order_id=razorpay_order['id'],
            status='created'
        )


    # Update existing payment with new order
    else:

        payment.razorpay_order_id = (
            razorpay_order['id']
        )

        payment.status = 'created'

        payment.save()


    context = {

        'booking': booking,

        'payment': payment,

        'razorpay_order_id': (
            razorpay_order['id']
        ),

        'razorpay_key_id': (
            settings.RAZORPAY_KEY_ID
        ),

        'amount_in_paise': amount_in_paise,

    }


    return render(
        request,
        'payments/payment.html',
        context
    )


@login_required
@require_POST
def verify_payment(request, booking_id):

    # User can only verify their own payment
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )


    payment = get_object_or_404(
        Payment,
        booking=booking
    )


    # Get payment data from POST request
    razorpay_payment_id = request.POST.get(
        'razorpay_payment_id'
    )

    razorpay_order_id = request.POST.get(
        'razorpay_order_id'
    )

    razorpay_signature = request.POST.get(
        'razorpay_signature'
    )


    # Ensure required payment data exists
    if not all([
        razorpay_payment_id,
        razorpay_order_id,
        razorpay_signature
    ]):

        messages.error(
            request,
            "Invalid payment response."
        )

        return redirect(
            'booking_detail',
            booking_id=booking.id
        )


    # Ensure the Razorpay order belongs to this payment
    if razorpay_order_id != payment.razorpay_order_id:

        messages.error(
            request,
            "Invalid payment order."
        )

        return redirect(
            'booking_detail',
            booking_id=booking.id
        )


    try:

        # Create Razorpay client
        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )


        # Verify payment signature
        client.utility.verify_payment_signature(
            {
                'razorpay_order_id': razorpay_order_id,

                'razorpay_payment_id': (
                    razorpay_payment_id
                ),

                'razorpay_signature': (
                    razorpay_signature
                ),

            }
        )


        # Update payment record
        payment.razorpay_payment_id = (
            razorpay_payment_id
        )

        payment.razorpay_signature = (
            razorpay_signature
        )

        payment.status = 'success'

        payment.save()


        # Confirm booking
        booking.status = 'confirmed'

        booking.save()


        messages.success(
            request,
            "Payment successful! Your booking is confirmed."
        )


        return redirect(
            'booking_detail',
            booking_id=booking.id
        )


    except razorpay.errors.SignatureVerificationError:

        payment.status = 'failed'

        payment.save()


        messages.error(
            request,
            "Payment verification failed."
        )


        return redirect(
            'booking_detail',
            booking_id=booking.id
        )