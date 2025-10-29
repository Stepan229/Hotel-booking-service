import pytest

from rest_framework.exceptions import ValidationError
from django.test import TestCase
from stay_manager.serializers import HotelSerializer, RoomSerializer, RoomBookingSerializer
from .factories import HotelCatalogFactory, RoomCatalogFactory

class TestHotelSerializer(TestCase):
    """Тесты с использованием unittest subTest"""
    
    def test_hotel_serializer_valid_cases(self):
        """Тест валидных данных"""
        test_cases = [
            {'name_hotel': 'Test Hotel'},
            {'name_hotel': 'Grand Plaza'},
            {'name_hotel': 'Hilton'},
        ]
        
        for valid_data in test_cases:
            with self.subTest(valid_data=valid_data):
                serializer = HotelSerializer(data=valid_data)
                self.assertTrue(serializer.is_valid())
                self.assertEqual(serializer.data['name_hotel'], valid_data['name_hotel'])
    
    def test_hotel_serializer_invalid_cases(self):
        """Тест невалидных данных"""
        test_cases = [
            ({'name_hotel': ''}, ['name_hotel']),
            ({}, ['name_hotel']),
            ({'name_hotel': 'A' * 1000}, ['name_hotel']),
        ]
        
        for invalid_data, expected_error_fields in test_cases:
            with self.subTest(invalid_data=invalid_data):
                serializer = HotelSerializer(data=invalid_data)
                self.assertFalse(serializer.is_valid())
                
                for error_field in expected_error_fields:
                    self.assertIn(error_field, serializer.errors)

class TestRoomSerializer(TestCase):
    def test_room_serializer_with_valid_data(self):
        hotel = HotelCatalogFactory()
        test_cases = [
            {
                'data': 
                    {
                        'hotel': hotel.id,
                        'room_description': 'Luxury Suite price 150',
                        'price': '150'
                    },
                'description': 'Luxury Suite',
            },
                        {
                'data': 
                    {
                        'hotel': hotel.id,
                        'room_description': 'Luxury Suite price 150',
                        'price': '150.0'
                    },
                'description': 'float price. sep .',
            },
        ]
        for case in test_cases:
            with self.subTest(data=case['data'], description=case['description']):
                serializer = RoomSerializer(data=case['data'])
                self.assertTrue(serializer.is_valid(), f"Failed test: data={case}")
                self.assertEqual(serializer.data['hotel'], case['data']['hotel'], f"Failed test: data={case}")

    def test_room_serializer_with_unvalid_data(self):
        hotel = HotelCatalogFactory()
        test_cases = [
            {
                'data': 
                    {
                        'hotel': '112345',  # invalid hotel id
                        'room_description': 'Luxury Suite price 150',
                        'price': '150'
                    },
                'description': 'inalid hotel id',
                'raise': ValidationError
            },
                        {
                'data': 
                    {
                        'hotel': '',
                        'room_description': 'Luxury Suite price 150',
                        'price': '150'
                    },
                'description': 'NONE hotel id',
                'raise': ValidationError
            },
                        {
                'data': 
                    {
                        'hotel': hotel.id,
                        'room_description': 'Luxury Suite price 150',
                        'price': '-150'
                    },
                'description': 'negative price',
                'raise': ValidationError
            },                        
            {
                'data': 
                    {
                        'hotel': hotel.id,
                        'room_description': 'Luxury Suite price 150',
                        'price': 'abc'
                    },
                'description': 'non-numeric price',
                'raise': ValidationError
            },
            {
                'data': 
                    {
                        'hotel': hotel.id,
                        'room_description': 'Luxury Suite price 150',
                        # missing price
                    },
                'description': 'missing price',
                'raise': ValidationError
            }
        ]
        for case in test_cases:
            with self.subTest(data=case['data'], description=case['description']):
                with self.assertRaises(case['raise']):
                    serializer = RoomSerializer(data=case['data'])
                    serializer.is_valid(raise_exception=True)
                
    
    def test_room_serializer_output(self):
        """Тест вывода сериализатора комнаты"""
        room = RoomCatalogFactory()
        serializer = RoomSerializer(room)
        self.assertEqual(serializer.data['id'], room.id)
        self.assertEqual(serializer.data['room_description'], room.room_description)
        self.assertEqual(serializer.data['price'], str(room.price))
        self.assertEqual(serializer.data['hotel'], room.hotel.id)

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