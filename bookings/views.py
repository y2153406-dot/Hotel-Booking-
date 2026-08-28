from datetime import datetime, date

from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST

from hotels.models import Room
from .models import Booking


@login_required
def create_booking(request, room_id):

    room = get_object_or_404(
        Room,
        id=room_id
    )


    if request.method == "POST":

        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        guests = request.POST.get('guests')


        # Check required fields
        if not check_in or not check_out or not guests:

            messages.error(
                request,
                "Please fill in all booking details."
            )

            return redirect(
                'create_booking',
                room_id=room.id
            )


        # Validate dates
        try:

            check_in_date = datetime.strptime(
                check_in,
                '%Y-%m-%d'
            ).date()

            check_out_date = datetime.strptime(
                check_out,
                '%Y-%m-%d'
            ).date()

        except ValueError:

            messages.error(
                request,
                "Please enter valid dates."
            )

            return redirect(
                'create_booking',
                room_id=room.id
            )


        # Validate guests
        try:

            guests = int(guests)

        except (ValueError, TypeError):

            messages.error(
                request,
                "Please enter a valid number of guests."
            )

            return redirect(
                'create_booking',
                room_id=room.id
            )


        # Guests must be at least 1
        if guests < 1:

            messages.error(
                request,
                "At least one guest is required."
            )

            return redirect(
                'create_booking',
                room_id=room.id
            )


        # Check-in date cannot be in the past
        if check_in_date < date.today():

            messages.error(
                request,
                "Check-in date cannot be in the past."
            )

            return redirect(
                'create_booking',
                room_id=room.id
            )


        # Check-out must be after check-in
        if check_out_date <= check_in_date:

            messages.error(
                request,
                "Check-out date must be after check-in date."
            )

            return redirect(
                'create_booking',
                room_id=room.id
            )


        # Guests cannot exceed room capacity
        if guests > room.capacity:

            messages.error(
                request,
                f"This room allows a maximum of {room.capacity} guests."
            )

            return redirect(
                'create_booking',
                room_id=room.id
            )


        # Check overlapping pending or confirmed bookings
        overlapping_bookings = Booking.objects.filter(
            room=room,
            check_in__lt=check_out_date,
            check_out__gt=check_in_date,
            status__in=['pending', 'confirmed']
        )


        # Check room availability
        if overlapping_bookings.count() >= room.total_rooms:

            messages.error(
                request,
                "Sorry, this room is not available for the selected dates."
            )

            return redirect(
                'create_booking',
                room_id=room.id
            )


        # Calculate total nights
        total_nights = (
            check_out_date - check_in_date
        ).days


        # Calculate total price
        total_price = (
            total_nights * room.price_per_night
        )


        # Create booking
        booking = Booking.objects.create(
            user=request.user,
            room=room,
            check_in=check_in_date,
            check_out=check_out_date,
            guests=guests,
            total_price=total_price,
            status='pending'
        )


        # Redirect to booking detail
        return redirect(
            'booking_detail',
            booking_id=booking.id
        )


    return render(
        request,
        'bookings/create_booking.html',
        {
            'room': room
        }
    )


@login_required
def my_bookings(request):

    bookings = Booking.objects.filter(
        user=request.user
    ).order_by('-created_at')


    return render(
        request,
        'bookings/my_bookings.html',
        {
            'bookings': bookings,
            'today': date.today()
        }
    )


@login_required
def booking_detail(request, booking_id):

    # User can only access their own booking
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )


    # Calculate total nights
    total_nights = (
        booking.check_out - booking.check_in
    ).days


    # Check whether a payment exists
    payment_exists = hasattr(
        booking,
        'payment'
    )


    return render(
        request,
        'bookings/booking_detail.html',
        {
            'booking': booking,
            'total_nights': total_nights,
            'today': date.today(),
            'payment_exists': payment_exists
        }
    )


@login_required
@require_POST
def cancel_booking(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )


    # Booking cannot be cancelled on or after check-in date
    if booking.check_in <= date.today():

        messages.error(
            request,
            "This booking can no longer be cancelled."
        )

        return redirect(
            'my_bookings'
        )


    # Only pending bookings can be cancelled
    if booking.status == 'pending':

        booking.status = 'cancelled'

        booking.save()


        messages.success(
            request,
            "Your booking has been cancelled successfully."
        )


    else:

        messages.error(
            request,
            "This booking cannot be cancelled."
        )


    return redirect(
        'my_bookings'
    )