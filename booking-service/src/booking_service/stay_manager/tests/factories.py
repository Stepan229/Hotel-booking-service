
from factory.declarations import LazyFunction, SubFactory
from django.utils import timezone
from factory.django import DjangoModelFactory
from stay_manager.models import HotelCatalog, RoomCatalog, RoomBooking
from faker import Faker
import datetime


fake =Faker()

class HotelCatalogFactory(DjangoModelFactory):
    class Meta:
        model = HotelCatalog

    name_hotel = LazyFunction(lambda: fake.company())

class RoomCatalogFactory(DjangoModelFactory):
    class Meta:
        model = RoomCatalog

    room_description = LazyFunction(lambda: fake.text(max_nb_chars=500))
    price = LazyFunction(lambda: round(fake.pydecimal(left_digits=3, right_digits=2, positive=True), 2))
    hotel = SubFactory(HotelCatalogFactory)
    created_at = LazyFunction(timezone.now)

class RoomBookingFactory(DjangoModelFactory):
    class Meta:
        model = RoomBooking

    room = SubFactory(RoomCatalogFactory)
    date_start = LazyFunction(lambda: timezone.now().date() + datetime.timedelta(days=1))
    date_end = LazyFunction(lambda: timezone.now().date() + datetime.timedelta(days=5))


    