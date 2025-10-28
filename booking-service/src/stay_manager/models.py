from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class HotelCatalog(models.Model):
    name_hotel = models.CharField(max_length=70)

    class Meta:
        app_label = 'stay_manager'
        
    def __str__(self):
        return str(self.name_hotel)


class RoomCatalog(models.Model):
    room_description = models.CharField(max_length=500, default='None')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    hotel = models.ForeignKey(HotelCatalog, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True )

    def __str__(self):
        return str(self.room_description)

class RoomBooking(models.Model):
    room = models.ForeignKey(RoomCatalog, on_delete=models.CASCADE)
    date_start = models.DateField()
    date_end = models.DateField()

    def __str__(self):
        return str(self.pk)