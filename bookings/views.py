from datetime import datetime, date

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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

        check_in_date = datetime.strptime(
            check_in,
            '%Y-%m-%d'
        ).date()

        check_out_date = datetime.strptime(
            check_out,
            '%Y-%m-%d'
        ).date()


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
        guests = int(guests)

        if guests > room.capacity:

            messages.error(
                request,
                f"This room allows a maximum of {room.capacity} guests."
            )

            return redirect(
                'create_booking',
                room_id=room.id
            )


        # Check overlapping confirmed or pending bookings
        overlapping_bookings = Booking.objects.filter(
            room=room,
            check_in__lt=check_out_date,
            check_out__gt=check_in_date,
            status__in=['pending', 'confirmed']
        )


        # Count already booked rooms
        booked_rooms = overlapping_bookings.count()


        # Check room availability
        if booked_rooms >= room.total_rooms:

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
        Booking.objects.create(
            user=request.user,
            room=room,
            check_in=check_in_date,
            check_out=check_out_date,
            guests=guests,
            total_price=total_price,
            status='pending'
        )


        messages.success(
            request,
            "Your booking has been created successfully!"
        )


        return redirect(
            'hotel_detail',
            id=room.hotel.id
        )


    context = {
        'room': room
    }


    return render(
        request,
        'bookings/create_booking.html',
        context
    )