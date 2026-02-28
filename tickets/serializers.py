from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Event, SubEvent, EntryType, StaffProfile, TicketCustomization, Ticket


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class StaffProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    staff_code = serializers.SerializerMethodField()
    assigned_sub_events = serializers.PrimaryKeyRelatedField(many=True, queryset=SubEvent.objects.all(), required=False)

    class Meta:
        model = StaffProfile
        fields = ['id', 'user', 'role', 'range_start', 'range_end', 'current_counter', 'staff_code', 'assigned_sub_events']

    def get_staff_code(self, obj):
        return obj.get_staff_code()


class CreateStaffSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    role = serializers.ChoiceField(choices=['admin', 'staff'], default='staff')
    range_start = serializers.IntegerField(min_value=1)
    range_end = serializers.IntegerField(min_value=1)

    def validate(self, data):
        if data['range_end'] <= data['range_start']:
            raise serializers.ValidationError("range_end must be greater than range_start")
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Username already exists")
        return data


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name', 'code', 'place', 'address', 'start_date', 'end_date', 'created_at']
        read_only_fields = ['code', 'created_at']

    def validate(self, data):
        if data['end_date'] < data['start_date']:
            raise serializers.ValidationError("end_date must be after start_date")
        return data


class SubEventSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source='event.name', read_only=True)
    
    class Meta:
        model = SubEvent
        fields = ['id', 'event', 'event_name', 'name', 'code', 'description', 'start_time', 'end_time', 'is_active', 'created_at']
        read_only_fields = ['code', 'created_at']

    def validate(self, data):
        if data['end_time'] <= data['start_time']:
            raise serializers.ValidationError("end_time must be after start_time")
        return data


class EntryTypeSerializer(serializers.ModelSerializer):
    sub_event_name = serializers.CharField(source='sub_event.name', read_only=True)
    event_name = serializers.CharField(source='sub_event.event.name', read_only=True)
    
    class Meta:
        model = EntryType
        fields = ['id', 'sub_event', 'sub_event_name', 'event_name', 'name', 'price', 'description', 'is_active']

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value


class TicketCustomizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketCustomization
        fields = ['id', 'event', 'header_text', 'footer_text', 'show_event_name', 
                  'show_place', 'show_entry_type', 'show_price', 'printer_format']


class TicketSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source='event.name', read_only=True)
    sub_event_name = serializers.CharField(source='sub_event.name', read_only=True)
    entry_type_name = serializers.CharField(source='entry_type.name', read_only=True)
    staff_username = serializers.CharField(source='staff.username', read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'ticket_id', 'event', 'event_name', 'sub_event', 'sub_event_name', 
                  'entry_type', 'entry_type_name', 'staff', 'staff_username', 'sequence_number', 'price', 'created_at']
        read_only_fields = ['ticket_id', 'sequence_number', 'created_at']


class GenerateTicketSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()
    sub_event_id = serializers.IntegerField()
    entry_type_id = serializers.IntegerField()

    def validate(self, data):
        try:
            event = Event.objects.get(id=data['event_id'])
        except Event.DoesNotExist:
            raise serializers.ValidationError("Event not found")

        try:
            sub_event = SubEvent.objects.get(id=data['sub_event_id'], event=event)
        except SubEvent.DoesNotExist:
            raise serializers.ValidationError("Sub-event not found for this event")

        if not sub_event.is_active:
            raise serializers.ValidationError("Sub-event is not active")

        try:
            entry_type = EntryType.objects.get(id=data['entry_type_id'], sub_event=sub_event)
        except EntryType.DoesNotExist:
            raise serializers.ValidationError("Entry type not found for this sub-event")

        if not entry_type.is_active:
            raise serializers.ValidationError("Entry type is not active")

        data['event'] = event
        data['sub_event'] = sub_event
        data['entry_type'] = entry_type
        return data


class TicketPrintSerializer(serializers.Serializer):
    """Serializer for ticket print response"""
    ticket_id = serializers.CharField()
    event_name = serializers.CharField()
    sub_event_name = serializers.CharField()
    place = serializers.CharField()
    entry_type = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    header_text = serializers.CharField()
    footer_text = serializers.CharField()
    created_at = serializers.DateTimeField()
    sequence_number = serializers.IntegerField()
