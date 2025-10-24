from rest_framework import serializers
from .models import HotelCatalog, RoomCatalog, RoomBooking

class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelCatalog
        fields = '__all__'
        


class RoomSerializer(serializers.ModelSerializer):
    hotel = serializers.PrimaryKeyRelatedField(
        queryset=HotelCatalog.objects.all()
    )
    class Meta:
        model = RoomCatalog
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be a non-negative value.")
        return value

    # def create(self, validated_data):
    #     print('Hotel: ', type(validated_data['hotel']))
    #     room = RoomCatalog.objects.create(room_description=validated_data['room_description'], 
    #                                     price=validated_data['price'], 
    #                                     hotel=validated_data['hotel'])
    #     return room

class RoomBookingSerializer(serializers.ModelSerializer):
    room = serializers.PrimaryKeyRelatedField(
        queryset=RoomCatalog.objects.all()
    )
    class Meta:
        model = RoomBooking
        fields = '__all__'

    def validate(self, attrs):
        self.validate_booking_dates(attrs['date_start'], attrs['date_end'], attrs['room'])
        return super().validate(attrs)
    
    @staticmethod
    def validate_booking_dates(date_start, date_end, room):
        if date_start > date_end:
            raise serializers.ValidationError("Booking start date cannot be later than end date.")
        between_bookings = RoomBooking.objects.filter(
            room=room,
            date_start__lt=date_end,
            date_end__gt=date_start
        )
        if between_bookings.exists():
            raise serializers.ValidationError("The room is already booked for the selected dates.")
        return True



