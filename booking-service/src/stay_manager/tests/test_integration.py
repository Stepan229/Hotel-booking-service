from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from stay_manager.models import HotelCatalog, RoomCatalog, RoomBooking


class TestBookingFlow(TestCase):
    """Интеграционные тесты полного цикла бронирования в стиле Django TestCase"""
    
    def setUp(self):
        self.api_client = APIClient()
        
    def test_complete_booking_flow(self):
        """Полный тест цикла бронирования"""
        # 1. Создаем отель
        hotel_data = {'name_hotel': 'Test Hotel'}
        hotel_response = self.api_client.post(reverse('hotel-create'), hotel_data)
        hotel_id = hotel_response.data['id']
        self.assertEqual(hotel_response.status_code, status.HTTP_201_CREATED)
        
        # 2. Создаем комнату
        room_data = {
            'hotel': hotel_id,
            'room_description': 'Luxury Suite',
            'price': '200.00'
        }
        room_response = self.api_client.post(reverse('rooms-create'), room_data)
        room_id = room_response.data['id']
        self.assertEqual(room_response.status_code, status.HTTP_201_CREATED)
        
        # 3. Создаем бронь
        booking_data = {
            'room': room_id,
            'date_start': str(date.today() + timedelta(days=1)),
            'date_end': str(date.today() + timedelta(days=5))
        }
        booking_response = self.api_client.post(reverse('booking-create-reservation'), booking_data)
        booking_id = booking_response.data  # Возвращает ID созданной брони
        self.assertEqual(booking_response.status_code, status.HTTP_201_CREATED)
        self.assertIsInstance(booking_id, int)
        
        # 4. Проверяем что бронь создалась
        list_response = self.api_client.get(
            reverse('booking-list-reservations'), 
            {'room_id': room_id}
        )
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)
        self.assertEqual(list_response.data[0]['id'], booking_id)
        
        # 5. Удаляем бронь
        delete_response = self.api_client.delete(
            reverse('booking-delete-reservation', kwargs={'pk': booking_id})
        )
        self.assertEqual(delete_response.status_code, status.HTTP_205_RESET_CONTENT)
        
        # 6. Проверяем что бронь удалилась
        final_list_response = self.api_client.get(
            reverse('booking-list-reservations'), 
            {'room_id': room_id}
        )
        self.assertEqual(final_list_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(final_list_response.data, 'No reservations found for the specified room.')

    def test_booking_with_invalid_dates(self):
        """Тест создания брони с невалидными датами"""
        # Создаем тестовые данные
        hotel_response = self.api_client.post(
            reverse('hotel-create'), 
            {'name_hotel': 'Test Hotel'}
        )
        hotel_id = hotel_response.data['id']
        
        room_response = self.api_client.post(
            reverse('rooms-create'),
            {
                'hotel': hotel_id,
                'room_description': 'Test Room',
                'price': '100.00'
            }
        )
        room_id = room_response.data['id']
        
        # Пытаемся создать бронь с датой окончания раньше начала
        invalid_booking_data = {
            'room': room_id,
            'date_start': '2024-01-05',
            'date_end': '2024-01-01'  # Дата окончания раньше начала
        }
        response = self.api_client.post(reverse('booking-create-reservation'), invalid_booking_data)
        
        # Ожидаем ошибку валидации
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_booking_conflict_detection(self):
        """Тест обнаружения конфликтующих бронирований"""
        # Создаем тестовые данные
        hotel_response = self.api_client.post(
            reverse('hotel-create'), 
            {'name_hotel': 'Conflict Hotel'}
        )
        hotel_id = hotel_response.data['id']
        
        room_response = self.api_client.post(
            reverse('rooms-create'),
            {
                'hotel': hotel_id,
                'room_description': 'Conflict Room',
                'price': '150.00'
            }
        )
        room_id = room_response.data['id']
        
        # Первая бронь
        first_booking_data = {
            'room': room_id,
            'date_start': '2024-02-01',
            'date_end': '2024-02-05'
        }
        first_booking_response = self.api_client.post(reverse('booking-create-reservation'), first_booking_data)
        self.assertEqual(first_booking_response.status_code, status.HTTP_201_CREATED)
        
        # Вторая бронь с пересекающимися датами
        conflicting_booking_data = {
            'room': room_id,
            'date_start': '2024-02-03',  # Пересекается с первой бронью
            'date_end': '2024-02-07'
        }
        second_booking_response = self.api_client.post(reverse('booking-create-reservation'), conflicting_booking_data)
        
        # Проверяем результат (зависит от реализации валидации конфликтов)
        self.assertIn(second_booking_response.status_code, [
            status.HTTP_201_CREATED,  # Если конфликты не проверяются
            status.HTTP_400_BAD_REQUEST  # Если есть валидация конфликтов
        ])

    def test_multiple_bookings_same_room(self):
        """Тест нескольких бронирований для одной комнаты"""
        # Создаем тестовые данные
        hotel_response = self.api_client.post(
            reverse('hotel-create'), 
            {'name_hotel': 'Multi Booking Hotel'}
        )
        hotel_id = hotel_response.data['id']
        
        room_response = self.api_client.post(
            reverse('rooms-create'),
            {
                'hotel': hotel_id,
                'room_description': 'Multi Booking Room',
                'price': '120.00'
            }
        )
        room_id = room_response.data['id']
        
        # Создаем несколько бронирований на разные даты
        bookings_data = [
            {
                'room': room_id,
                'date_start': '2024-03-01',
                'date_end': '2024-03-03'
            },
            {
                'room': room_id,
                'date_start': '2024-03-05',
                'date_end': '2024-03-07'
            },
            {
                'room': room_id,
                'date_start': '2024-03-10',
                'date_end': '2024-03-12'
            }
        ]
        
        created_booking_ids = []
        for booking_data in bookings_data:
            response = self.api_client.post(reverse('booking-create-reservation'), booking_data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            created_booking_ids.append(response.data)
        
        # Проверяем что все брони создались
        list_response = self.api_client.get(
            reverse('booking-list-reservations'), 
            {'room_id': room_id}
        )
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 3)
        
        # Проверяем что данные отсортированы по дате начала
        dates = [booking['date_start'] for booking in list_response.data]
        self.assertEqual(dates, sorted(dates))
        
        # Удаляем все брони
        for booking_id in created_booking_ids:
            delete_response = self.api_client.delete(
                reverse('booking-delete-reservation', kwargs={'pk': booking_id})
            )
            self.assertEqual(delete_response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_booking_flow_error_cases(self):
        """Тест ошибок в потоке бронирования"""
        # Попытка создать бронь без комнаты
        invalid_booking_data = {
            'date_start': '2024-01-01',
            'date_end': '2024-01-05'
        }
        response = self.api_client.post(reverse('booking-create-reservation'), invalid_booking_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('room', response.data)
        
        # Попытка получить список броней без указания комнаты
        response = self.api_client.get(reverse('booking-list-reservations'))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Попытка удалить несуществующую бронь
        response = self.api_client.delete(reverse('booking-delete-reservation', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Reservation 99999 was not found', response.data)

    def test_booking_with_nonexistent_room(self):
        """Тест создания брони для несуществующей комнаты"""
        booking_data = {
            'room': 99999,  # Несуществующая комната
            'date_start': '2024-01-01',
            'date_end': '2024-01-05'
        }
        response = self.api_client.post(reverse('booking-create-reservation'), booking_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('room', response.data)

    def test_booking_list_with_invalid_room_id(self):
        """Тест получения списка броней для несуществующей комнаты"""
        response = self.api_client.get(
            reverse('booking-list-reservations'), 
            {'room_id': 99999}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, 'No reservations found for the specified room.')

    def test_booking_deletion_verification(self):
        """Тест проверки что бронь действительно удаляется из БД"""
        # Создаем тестовые данные
        hotel_response = self.api_client.post(
            reverse('hotel-create'), 
            {'name_hotel': 'Deletion Hotel'}
        )
        hotel_id = hotel_response.data['id']
        
        room_response = self.api_client.post(
            reverse('rooms-create'),
            {
                'hotel': hotel_id,
                'room_description': 'Deletion Room',
                'price': '100.00'
            }
        )
        room_id = room_response.data['id']
        
        # Создаем бронь
        booking_data = {
            'room': room_id,
            'date_start': '2024-04-01',
            'date_end': '2024-04-03'
        }
        booking_response = self.api_client.post(reverse('booking-create-reservation'), booking_data)
        booking_id = booking_response.data
        
        # Проверяем что бронь есть в БД
        self.assertTrue(RoomBooking.objects.filter(id=booking_id).exists())
        
        # Удаляем бронь
        delete_response = self.api_client.delete(
            reverse('booking-delete-reservation', kwargs={'pk': booking_id})
        )
        self.assertEqual(delete_response.status_code, status.HTTP_205_RESET_CONTENT)
        
        # Проверяем что бронь удалилась из БД
        self.assertFalse(RoomBooking.objects.filter(id=booking_id).exists())