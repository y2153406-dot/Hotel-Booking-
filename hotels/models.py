from django.db import models


class Hotel(models.Model):
    name = models.CharField(max_length=200)

    location = models.CharField(max_length=200)

    description = models.TextField()

    image = models.ImageField(upload_to='hotels/')


    def __str__(self):
        return self.name


class Room(models.Model):
    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name='rooms'
    )

    room_type = models.CharField(max_length=100)

    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    capacity = models.PositiveIntegerField()

    total_rooms = models.PositiveIntegerField(
        default=1
    )

    description = models.TextField()

    image = models.ImageField(
        upload_to='rooms/'
    )


    def __str__(self):
        return f"{self.hotel.name} - {self.room_type}"