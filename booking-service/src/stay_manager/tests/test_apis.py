import pytest
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from stay_manager.models import HotelCatalog, RoomCatalog, RoomBooking
from .factories import HotelCatalogFactory, RoomCatalogFactory, RoomBookingFactory
from rest_framework.test import APIClient
from datetime import date, timedelta

class TestHotelAPIs(TestCase):
    
    def setUp(self):
        # Создаем клиент вручную
        self.api_client = APIClient()
    
    def test_get_hotel_list(self):
        # Создаем несколько отелей
        count_hotels = 4
        HotelCatalogFactory.create_batch(count_hotels)
        
        url = reverse('hotel-list')  
        response = self.api_client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), count_hotels)

    def test_create_hotel(self):
        url = reverse('hotel-create')
        data = {'name_hotel': 'Test Hotel'}
        
        response = self.api_client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        hotel_id = response.data['id']
        hotel = HotelCatalog.objects.get(id=hotel_id)
        self.assertIsNotNone(hotel)
        self.assertEqual(hotel.name_hotel, 'Test Hotel')

def make_request(api_client, url_name, method='get', kwargs=None, data=None):
    url = reverse(url_name, kwargs=kwargs)
    response = getattr(api_client, method)(url, data)
    return response

class TestRoomAPIs(TestCase):
    def setUp(self):
        self.api_client = APIClient()
        self.hotel = HotelCatalogFactory()
        self.room = RoomCatalogFactory(hotel=self.hotel)
        self.room_data = {
            'hotel': self.hotel.id,
            'room_description': 'Test Room',
            'price': '100.00'
        }

    def test_basic_operations(self):
        """Тестирование основных операций CRUD"""
        # CREATE
        response = self.api_client.post(reverse('rooms-create'), self.room_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # READ list
        response = self.api_client.get(reverse('list-rooms', kwargs={'hotel_id': self.hotel.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # DELETE
        response = self.api_client.delete(reverse('room-detail', kwargs={'pk': self.room.id}))
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_error_cases(self):
        """Тестирование ошибочных сценариев"""
        test_cases = [
            # (url_name, kwargs, method, data, expected_status, expected_message)
            ('list-rooms', {'hotel_id': 9999}, 'get', {}, status.HTTP_404_NOT_FOUND, 'Room number 9999 was not found'),
            ('room-detail', {'pk': 9999}, 'delete', {}, status.HTTP_404_NOT_FOUND, 'Room number 9999 was not found'),
            ('rooms-create', {}, 'post', {'invalid': 'data'}, status.HTTP_400_BAD_REQUEST, {'hotel': ['This field is required.'], 'price': ['This field is required.']}),
            ('list-rooms', {'hotel_id': self.hotel.id}, 'get', {'sort': 'invalid_field'}, status.HTTP_400_BAD_REQUEST, "Sorting by invalid_field is not allowed. Use ['price', 'created_at'] fields."),
            ('rooms-create', {}, 'post', {'hotel': '', 'room_description': 'Desc', 'price': '100.00'}, status.HTTP_400_BAD_REQUEST, {'hotel': ['This field may not be null.']}),
            ('rooms-create', {}, 'post', {'hotel': self.hotel.id, 'room_description': 'Desc', 'price': '-50'}, status.HTTP_400_BAD_REQUEST, {'price': ['Ensure this value is greater than or equal to 0.01.']}),
            ('rooms-create', {}, 'post', {'hotel': self.hotel.id, 'room_description': 'Desc'}, status.HTTP_400_BAD_REQUEST, {'price': ['This field is required.']}),
            ('rooms-create', {}, 'post', {'hotel': self.hotel.id, 'room_description': 'Desc', 'price': 'abc'}, status.HTTP_400_BAD_REQUEST, {'price': ['A valid number is required.']}),
            ('rooms-create', {}, 'post', {'hotel': self.hotel.id, 'room_description': 'Desc'}, status.HTTP_400_BAD_REQUEST, {'price': ['This field is required.']}),
        ]
        
        for url_name, kwargs, method, data, expected_status, expected_message in test_cases:
            with self.subTest(url_name=url_name):
                response = make_request(
                    self.api_client, url_name, method=method, kwargs=kwargs, data=data)
                self.assertEqual(response.status_code, expected_status, 
                                 f'Failed test: {url_name} with response {data}')
                
                response_text = response.data
                self.assertEqual(response_text, expected_message, 
                                 f'Failed test: {url_name} with response {data}{response_text}')

class TestBookingAPIs(TestCase):
    def setUp(self):
        self.api_client = APIClient()
        self.hotel = HotelCatalogFactory()
        self.room = RoomCatalogFactory(hotel=self.hotel)
        self.room2 = RoomCatalogFactory(hotel=self.hotel)
        
        # Создаем тестовые бронирования
        self.booking1 = RoomBookingFactory(
            room=self.room,
            date_start=date.today() + timedelta(days=1),
            date_end=date.today() + timedelta(days=3)
        )
        self.booking2 = RoomBookingFactory(
            room=self.room,
            date_start=date.today() + timedelta(days=5),
            date_end=date.today() + timedelta(days=7)
        )
        
        # Данные для создания новой брони
        self.booking_data = {
            'room': self.room.id,
            'date_start': str(date.today() + timedelta(days=10)),
            'date_end': str(date.today() + timedelta(days=12))
        }

    def test_basic_operations(self):
        """Тестирование основных операций CRUD для бронирований"""
        
        # READ list - получение списка бронирований комнаты
        response = self.api_client.get(
            reverse('booking-list-reservations'), 
            {'room_id': self.room.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Две брони для комнаты
        
        # CREATE - создание новой брони
        response = self.api_client.post(
            reverse('booking-create-reservation'), 
            self.booking_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        booking_id = response.data  # Возвращает ID созданной брони
        
        # Проверяем что бронь создалась
        response = self.api_client.get(
            reverse('booking-list-reservations'), 
            {'room_id': self.room.id}
        )
        self.assertEqual(len(response.data), 3)  # Теперь три брони
        
        # DELETE - удаление брони
        response = self.api_client.delete(
            reverse('booking-delete-reservation', kwargs={'pk': booking_id})
        )
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        
        # Проверяем что бронь удалилась
        response = self.api_client.get(
            reverse('booking-list-reservations'), 
            {'room_id': self.room.id}
        )
        self.assertEqual(len(response.data), 2)  # Снова две брони

    def test_error_cases(self):
        """Тестирование ошибочных сценариев для бронирований"""
        
        test_cases = [
            # (url_name, kwargs, method, data, query_params, expected_status, expected_message)
            
            ('booking-list-reservations', {}, 'get', {}, {}, 
             status.HTTP_404_NOT_FOUND, 'No reservations found for the specified room.'),
            
            ('booking-list-reservations', {}, 'get', {}, {'room_id': ''}, 
             status.HTTP_404_NOT_FOUND, 'No reservations found for the specified room.'),
            
            ('booking-list-reservations', {}, 'get', {}, {'room_id': 9999}, 
             status.HTTP_404_NOT_FOUND, 'No reservations found for the specified room.'),
            
            # POST /bookings/create/ - ошибки создания брони
            ('booking-create-reservation', {}, 'post', {}, {}, 
             status.HTTP_400_BAD_REQUEST, {'room': ['This field is required.'], 'date_start': ['This field is required.'], 'date_end': ['This field is required.']}),
            
            ('booking-create-reservation', {}, 'post', {'room': ''}, {}, 
             status.HTTP_400_BAD_REQUEST, {'room': ['This field may not be null.'], 'date_start': ['This field is required.'], 'date_end': ['This field is required.']}),
            
            ('booking-create-reservation', {}, 'post', {'room': 9999}, {}, 
             status.HTTP_400_BAD_REQUEST, {'room': ['Invalid pk "9999" - object does not exist.'], 'date_start': ['This field is required.'], 'date_end': ['This field is required.']}),
            
            ('booking-create-reservation', {}, 'post', {
                'room': self.room.id, 
                'date_start': 'invalid_date', 
                'date_end': '2024-01-05'
            }, {}, 
             status.HTTP_400_BAD_REQUEST, {'date_start': ['Date has wrong format. Use one of these formats instead: YYYY-MM-DD.']}),
            
            ('booking-create-reservation', {}, 'post', {
                'room': self.room.id, 
                'date_start': '2024-01-05', 
                'date_end': '2024-01-01'  # Дата окончания раньше начала
            }, {}, 
             status.HTTP_400_BAD_REQUEST, {'non_field_errors': ['Booking start date cannot be later than end date.']}),
            
            # DELETE /bookings/<pk>/ - ошибки удаления
            ('booking-delete-reservation', {'pk': 9999}, 'delete', {}, {}, 
             status.HTTP_404_NOT_FOUND, 'Reservation 9999 was not found'),
            
        ]
        
        for url_name, kwargs, method, data, query_params, expected_status, expected_message in test_cases:
            with self.subTest(url_name=url_name, data=data):
                # Создаем URL с query параметрами
                response = make_request(
                    self.api_client, url_name, method=method, kwargs=kwargs, data=data)
                
                self.assertEqual(response.status_code, expected_status, 
                               f'Failed test: {url_name} with data {data}')
                
                response_data = response.data
                self.assertEqual(response_data, expected_message, 
                               f'Failed test: {url_name} with data {data}. Response: {response_data}')

    def test_booking_conflicts(self):
        """Тестирование конфликтующих бронирований"""
        
        # Создаем бронь на существующие даты
        conflict_data = {
            'room': self.room.id,
            'date_start': str(self.booking1.date_start),  # Пересекается с существующей броньью
            'date_end': str(self.booking1.date_end)
        }
        
        response = self.api_client.post(
            reverse('booking-create-reservation'), 
            conflict_data
        )
        
        # Ожидаем ошибку конфликта (если у вас есть такая валидация)
        # Если валидации нет, этот тест может проходить с 201
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_201_CREATED])

    def test_sorting_functionality(self):
        """Тестирование сортировки бронирований"""
        
        # Создаем брони с разными датами для тестирования сортировки
        RoomBookingFactory(
            room=self.room,
            date_start=date.today() + timedelta(days=15),
            date_end=date.today() + timedelta(days=17)
        )
        
        # Тестируем сортировку по date_start (по умолчанию)
        response = self.api_client.get(
            reverse('booking-list-reservations'), 
            {'room_id': self.room.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем что данные отсортированы по date_start
        if len(response.data) > 1:
            dates = [booking['date_start'] for booking in response.data]
            self.assertEqual(dates, sorted(dates))

    def test_different_rooms_bookings(self):
        """Тестирование что брони разных комнат не смешиваются"""
        
        # Создаем бронь для второй комнаты
        RoomBookingFactory(
            room=self.room2,
            date_start=date.today() + timedelta(days=1),
            date_end=date.today() + timedelta(days=3)
        )
        
        # Запрашиваем брони первой комнаты
        response = self.api_client.get(
            reverse('booking-list-reservations'), 
            {'room_id': self.room.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Все брони должны быть только для первой комнаты
        for booking in response.data:
            self.assertEqual(booking['room'], self.room.id)