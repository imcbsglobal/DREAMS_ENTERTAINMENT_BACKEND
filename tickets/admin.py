from django.contrib import admin
from .models import Event, SubEvent, EntryType, StaffProfile, TicketCustomization, Ticket


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'place', 'start_date', 'end_date', 'created_at']
    search_fields = ['name', 'code', 'place']
    list_filter = ['start_date', 'end_date']
    readonly_fields = ['code', 'created_at']


@admin.register(SubEvent)
class SubEventAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'event', 'start_time', 'end_time', 'is_active', 'created_at']
    search_fields = ['name', 'code', 'event__name']
    list_filter = ['event', 'is_active', 'start_time']
    readonly_fields = ['code', 'created_at']


@admin.register(EntryType)
class EntryTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'sub_event', 'price', 'is_active']
    list_filter = ['sub_event__event', 'is_active']
    search_fields = ['name', 'sub_event__name']


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'range_start', 'range_end', 'current_counter']
    list_filter = ['role']
    search_fields = ['user__username', 'user__email']


@admin.register(TicketCustomization)
class TicketCustomizationAdmin(admin.ModelAdmin):
    list_display = ['event', 'show_event_name', 'show_place', 'show_entry_type', 'show_price']
    list_filter = ['show_event_name', 'show_place', 'show_entry_type', 'show_price']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_id', 'event', 'sub_event', 'entry_type', 'staff', 'price', 'created_at']
    list_filter = ['event', 'sub_event', 'entry_type', 'created_at']
    search_fields = ['ticket_id', 'staff__username']
    readonly_fields = ['ticket_id', 'created_at']
