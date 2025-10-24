from django.test import TestCase
from stay_manager.serializers import HotelSerializer, RoomSerializer, RoomBookingSerializer
from .factories import HotelCatalogFactory, RoomCatalogFactory

class TestHotelSerializer(TestCase):
    def test_hotel_serializer_valid_data(self):
        """Тест валидных данных сериализатора отеля"""
        data = {
            'name_hotel': 'Test Hotel',
            'address': 'Test Address'
        }
        serializer = HotelSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_hotel_serializer_invalid_data(self):
        """Тест невалидных данных сериализатора отеля"""
        data = {
            'name_hotel': '',
            'address': 'Test Address'
        }
        serializer = HotelSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertTrue('name_hotel' in serializer.errors)

class TestRoomSerializer(TestCase):
    def test_room_serializer_with_valid_data(self):
        """Тест сериализатора комнаты с валидными данными"""
        hotel = HotelCatalogFactory()
        data = {
            'hotel': hotel.id,
            'room_description': 'Luxury Suite',
            'price': '150.00'
        }
        serializer = RoomSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_room_serializer_output(self):
        """Тест вывода сериализатора комнаты"""
        room = RoomCatalogFactory()
        serializer = RoomSerializer(room)
        assert 'id' in serializer.data
        assert 'hotel' in serializer.data
        assert 'price' in serializer.data

class TestBookingSerializer(TestCase):
    def test_booking_serializer_date_validation(self):
        """Тест валидации дат в сериализаторе брони"""
        room = RoomCatalogFactory()
        data = {
            'room': room.id,
            'guest_name': 'John Doe',
            'date_start': '2024-01-10',
            'date_end': '2024-01-05'  # Дата окончания раньше начала
        }
        serializer = RoomBookingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        assert 'non_field_errors' in serializer.errors