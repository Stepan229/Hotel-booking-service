
from django.core.exceptions import ValidationError
from django.test import TestCase
from ..models import HotelCatalog, RoomCatalog, RoomBooking
from .factories import HotelCatalogFactory, RoomCatalogFactory, RoomBookingFactory



class TestHotelCatalogModel(TestCase):
    def test_create_hotel_catalog(self):
        hotel = HotelCatalogFactory()
        self.assertIsInstance(hotel, HotelCatalog)
        self.assertTrue(len(hotel.name_hotel) > 0)

    def test_str_hotel_representaion(self):
        hotel = HotelCatalogFactory(name_hotel="Test Hotel")
        self.assertEqual(str(hotel.name_hotel), "Test Hotel")


class TestRoomCatalogModel(TestCase):
    def test_create_room_catalog(self):
        room = RoomCatalogFactory()
        self.assertIsInstance(room, RoomCatalog)
        self.assertTrue(len(room.room_description) > 0)
        self.assertGreater(room.price, 0)
        self.assertIsInstance(room.hotel, HotelCatalog)

    def test_str_room_representaion(self):
        room = RoomCatalogFactory()
        self.assertEqual(str(room.pk), str(room.pk))

    def test_room_price_positive(self):
        with self.assertRaises(ValidationError):
            room = RoomCatalogFactory(price=-100)
            room.full_clean()

class TestRoomBookingModel(TestCase):
    def test_create_room_booking(self):
        booking = RoomBookingFactory()
        self.assertIsInstance(booking, RoomBooking)
        self.assertIsInstance(booking.room, RoomCatalog)
        self.assertLess(booking.date_start, booking.date_end)

    def test_str_booking_representaion(self):
        booking = RoomBookingFactory()
        self.assertEqual(str(booking.pk), str(booking.pk))

        
