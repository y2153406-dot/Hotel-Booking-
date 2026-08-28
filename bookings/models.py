from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, F

from hotels.models import Room


class Booking(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]


    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )


    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE
    )


    check_in = models.DateField()


    check_out = models.DateField()


    guests = models.PositiveIntegerField()


    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )


    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    class Meta:

        constraints = [

            models.CheckConstraint(
                condition=Q(guests__gte=1),
                name='booking_guests_at_least_one'
            ),

            models.CheckConstraint(
                condition=Q(check_out__gt=F('check_in')),
                name='booking_check_out_after_check_in'
            ),

        ]


    def __str__(self):

        return (
            f"{self.user.username} - "
            f"{self.room.room_type}"
        )