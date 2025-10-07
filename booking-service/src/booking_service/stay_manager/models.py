from django.db import models


class HotelCatalog(models.Model):
    name_hotel = models.CharField(max_length=70)


class RoomCatalog(models.Model):
    room_description = models.CharField(max_length=500, default='None')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    hotel = models.ForeignKey(HotelCatalog, on_delete=models.CASCADE)

    def __str__(self):
        return self.id

class RoomBooking(models.Model):
    room = models.ForeignKey(RoomCatalog, on_delete=models.CASCADE)
    date_start = models.DateField()
    date_end = models.DateField()

    def __str__(self):
        return self.id
