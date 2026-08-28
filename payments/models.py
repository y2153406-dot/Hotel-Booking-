from django.db import models

from bookings.models import Booking


class Payment(models.Model):

    PAYMENT_STATUS_CHOICES = [

        ('created', 'Created'),

        ('success', 'Success'),

        ('failed', 'Failed'),

    ]


    booking = models.OneToOneField(

        Booking,

        on_delete=models.CASCADE,

        related_name='payment'

    )


    razorpay_order_id = models.CharField(

        max_length=255,

        blank=True,

        null=True

    )


    razorpay_payment_id = models.CharField(

        max_length=255,

        blank=True,

        null=True

    )


    razorpay_signature = models.CharField(

        max_length=500,

        blank=True,

        null=True

    )


    amount = models.DecimalField(

        max_digits=10,

        decimal_places=2

    )


    status = models.CharField(

        max_length=20,

        choices=PAYMENT_STATUS_CHOICES,

        default='created'

    )


    created_at = models.DateTimeField(

        auto_now_add=True

    )


    def __str__(self):

        return f"Payment for Booking #{self.booking.id}"