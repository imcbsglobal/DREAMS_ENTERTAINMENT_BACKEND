from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Sum, Count, Q
from django.utils import timezone
from .models import Event, SubEvent, EntryType, StaffProfile, TicketCustomization, Ticket, SubEventMaster
from .serializers import (
    EventSerializer, SubEventSerializer, EntryTypeSerializer, StaffProfileSerializer,
    CreateStaffSerializer, TicketCustomizationSerializer, TicketSerializer,
    GenerateTicketSerializer, TicketPrintSerializer, SubEventMasterSerializer
)
from .permissions import IsAdmin, IsStaff, IsAdminOrStaff
from .services import TicketService


# ==================== ADMIN VIEWS ====================

class CreateStaffView(APIView):
    """Admin: Create staff user with profile"""
    permission_classes = [IsAdmin]

    @transaction.atomic
    def post(self, request):
        serializer = CreateStaffSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            # Create user
            user = User.objects.create_user(
                username=data['username'],
                password=data['password'],
                email=data['email'],
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', '')
            )
            
            # Create staff profile
            staff_profile = StaffProfile.objects.create(
                user=user,
                role=data['role'],
                range_start=data['range_start'],
                range_end=data['range_end'],
                current_counter=0
            )
            
            return Response({
                'message': 'Staff created successfully',
                'data': StaffProfileSerializer(staff_profile).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateStaffView(APIView):
    """Admin: Update staff with conditional editing based on ticket generation"""
    permission_classes = [IsAdmin]
    
    @transaction.atomic
    def put(self, request, staff_id):
        try:
            staff_profile = StaffProfile.objects.get(id=staff_id)
            user = staff_profile.user
            
            # Check if staff has generated any tickets
            tickets_count = Ticket.objects.filter(staff=user).count()
            has_generated_tickets = tickets_count > 0
            
            if has_generated_tickets:
                # RESTRICTED EDITING - Only safe fields
                return self._handle_restricted_edit(staff_profile, request.data, tickets_count)
            else:
                # FULL EDITING - All fields allowed
                return self._handle_full_edit(staff_profile, request.data)
                
        except StaffProfile.DoesNotExist:
            return Response({'error': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def _handle_restricted_edit(self, staff_profile, data, tickets_count):
        """Handle editing for staff who have generated tickets"""
        
        # Define allowed fields for staff with tickets
        ALLOWED_FIELDS = [
            'first_name', 'last_name', 'email',  # User personal info
            'assigned_sub_events',                # Sub-event assignments
            'password'                           # Allow password changes
        ]
        
        # Check for restricted fields
        restricted_fields = []
        for field in data.keys():
            if field not in ALLOWED_FIELDS:
                restricted_fields.append(field)
        
        if restricted_fields:
            return Response({
                'error': 'Cannot edit these fields for staff with existing tickets',
                'details': {
                    'tickets_generated': tickets_count,
                    'restricted_fields': restricted_fields,
                    'allowed_fields': ALLOWED_FIELDS,
                    'reason': 'Staff has generated tickets - only safe fields can be edited'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update only allowed fields
        user = staff_profile.user
        updated_fields = []
        
        # Update User fields
        if 'first_name' in data:
            user.first_name = data['first_name']
            updated_fields.append('first_name')
        if 'last_name' in data:
            user.last_name = data['last_name']
            updated_fields.append('last_name')
        if 'email' in data:
            user.email = data['email']
            updated_fields.append('email')
        if 'password' in data:
            user.set_password(data['password'])
            updated_fields.append('password')
        
        user.save()
        
        # Update sub-event assignments
        if 'assigned_sub_events' in data:
            staff_profile.assigned_sub_events.set(data['assigned_sub_events'])
            updated_fields.append('assigned_sub_events')
        
        return Response({
            'message': 'Staff updated successfully (restricted mode)',
            'note': f'Limited editing due to {tickets_count} generated tickets',
            'updated_fields': updated_fields,
            'data': StaffProfileSerializer(staff_profile).data
        })
    
    def _handle_full_edit(self, staff_profile, data):
        """Handle full editing for new staff with no tickets"""
        
        user = staff_profile.user
        
        # Validate all fields
        validation_errors = self._validate_full_edit(staff_profile, data)
        if validation_errors:
            return Response({'errors': validation_errors}, status=status.HTTP_400_BAD_REQUEST)
        
        updated_fields = []
        
        # Update User fields
        user_fields = ['username', 'first_name', 'last_name', 'email', 'password']
        for field in user_fields:
            if field in data:
                if field == 'password':
                    user.set_password(data[field])
                else:
                    setattr(user, field, data[field])
                updated_fields.append(field)
        user.save()
        
        # Update StaffProfile fields
        profile_fields = ['role', 'range_start', 'range_end']
        for field in profile_fields:
            if field in data:
                setattr(staff_profile, field, data[field])
                updated_fields.append(field)
        
        # Update sub-event assignments
        if 'assigned_sub_events' in data:
            staff_profile.assigned_sub_events.set(data['assigned_sub_events'])
            updated_fields.append('assigned_sub_events')
        
        staff_profile.save()
        
        return Response({
            'message': 'Staff updated successfully (full edit mode)',
            'note': 'All fields editable - no tickets generated yet',
            'updated_fields': updated_fields,
            'data': StaffProfileSerializer(staff_profile).data
        })
    
    def _validate_full_edit(self, staff_profile, data):
        """Validate full edit data"""
        errors = {}
        
        # Username validation
        if 'username' in data:
            if User.objects.filter(username=data['username']).exclude(id=staff_profile.user.id).exists():
                errors['username'] = 'Username already exists'
        
        # Range validation
        if 'range_start' in data and 'range_end' in data:
            if data['range_end'] <= data['range_start']:
                errors['range'] = 'range_end must be greater than range_start'
        elif 'range_start' in data:
            if data['range_start'] >= staff_profile.range_end:
                errors['range_start'] = 'range_start must be less than current range_end'
        elif 'range_end' in data:
            if data['range_end'] <= staff_profile.range_start:
                errors['range_end'] = 'range_end must be greater than current range_start'
        
        # Role validation
        if 'role' in data and data['role'] not in ['admin', 'staff']:
            errors['role'] = 'Role must be admin or staff'
        
        # Password validation
        if 'password' in data and len(data['password']) < 6:
            errors['password'] = 'Password must be at least 6 characters long'
        
        return errors


class DeleteStaffView(APIView):
    """Admin: Delete staff (soft delete using User.is_active)"""
    permission_classes = [IsAdmin]
    
    def delete(self, request, staff_id):
        try:
            staff_profile = StaffProfile.objects.get(id=staff_id)
            user = staff_profile.user
            
            # Get stats before deletion
            tickets_count = Ticket.objects.filter(staff=user).count()
            total_revenue = Ticket.objects.filter(staff=user).aggregate(
                total=Sum('price')
            )['total'] or 0
            
            # Store info for response
            username = user.username
            staff_code = staff_profile.get_staff_code()
            
            # Soft delete - deactivate user (preserves all tickets and reports)
            user.is_active = False
            user.save()
            
            # Clear sub-event assignments
            staff_profile.assigned_sub_events.clear()
            
            return Response({
                'message': f'Staff "{username}" deleted successfully',
                'preserved_data': {
                    'tickets_preserved': tickets_count,
                    'revenue_preserved': str(total_revenue),
                    'staff_code': staff_code,
                    'note': 'All tickets and reports remain intact. Staff cannot login but data is preserved.'
                }
            })
            
        except StaffProfile.DoesNotExist:
            return Response({'error': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)


class StaffListView(generics.ListAPIView):
    """Admin: List all active staff"""
    permission_classes = [IsAdmin]
    serializer_class = StaffProfileSerializer
    
    def get_queryset(self):
        # Only show staff with active users (excludes soft-deleted staff)
        return StaffProfile.objects.filter(user__is_active=True)


class AssignEventsToStaffView(APIView):
    """Admin: Assign sub-events to staff"""
    permission_classes = [IsAdmin]

    def post(self, request):
        staff_id = request.data.get('staff_id')
        sub_event_ids = request.data.get('sub_event_ids', [])
        replace = request.data.get('replace', True)  # Default: replace all

        try:
            staff_profile = StaffProfile.objects.get(id=staff_id)
            
            if staff_profile.role != 'staff':
                return Response({'error': 'Can only assign sub-events to staff role'}, status=status.HTTP_400_BAD_REQUEST)
            
            if replace:
                # Replace all assignments
                staff_profile.assigned_sub_events.set(sub_event_ids)
            else:
                # Add to existing assignments
                staff_profile.assigned_sub_events.add(*sub_event_ids)
            
            current_assignments = list(staff_profile.assigned_sub_events.values_list('id', flat=True))
            
            return Response({
                'message': 'Sub-events assigned successfully',
                'staff_id': staff_id,
                'assigned_sub_events': current_assignments
            })
        except StaffProfile.DoesNotExist:
            return Response({'error': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)


class PredefinedSubEventsView(APIView):
    """Admin: Get predefined sub-events list from database"""
    permission_classes = [IsAdmin]
    
    def get(self, request):
        # Fetch active sub-events from master data
        master_sub_events = SubEventMaster.objects.filter(is_active=True).order_by('name')
        predefined_sub_events = [item.name for item in master_sub_events]
        
        return Response({
            'predefined_sub_events': predefined_sub_events
        })


class CreateEventView(APIView):
    """Admin: Create event with optional sub-events selection"""
    permission_classes = [IsAdmin]

    @transaction.atomic
    def post(self, request):
        # Extract sub-events from request data
        event_data = request.data.copy()
        selected_sub_events = event_data.pop('selected_sub_events', [])
        
        # Validate event data
        serializer = EventSerializer(data=event_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Create event with flag to skip auto sub-event creation
        event = serializer.save()
        event._skip_auto_subevent = True
        
        # Create selected sub-events or default
        if selected_sub_events:
            created_sub_events = self._create_selected_sub_events(event, selected_sub_events)
        else:
            # Create default ENTRY TICKET if no selection
            created_sub_events = self._create_default_sub_event(event)
        
        return Response({
            'message': 'Event created successfully',
            'event': EventSerializer(event).data,
            'sub_events': SubEventSerializer(created_sub_events, many=True).data
        }, status=status.HTTP_201_CREATED)
    
    def _create_selected_sub_events(self, event, selected_names):
        """Create sub-events for selected names"""
        from datetime import datetime, time
        
        created_sub_events = []
        start_time = datetime.combine(event.start_date, time(9, 0))
        end_time = datetime.combine(event.end_date, time(23, 59))
        
        for name in selected_names:
            sub_event = SubEvent.objects.create(
                event=event,
                name=name,
                description=f'{name} for {event.name}',
                start_time=start_time,
                end_time=end_time,
                is_active=True
            )
            created_sub_events.append(sub_event)
        
        return created_sub_events
    
    def _create_default_sub_event(self, event):
        """Create default ENTRY TICKET sub-event"""
        from datetime import datetime, time
        
        start_time = datetime.combine(event.start_date, time(9, 0))
        end_time = datetime.combine(event.end_date, time(23, 59))
        
        sub_event = SubEvent.objects.create(
            event=event,
            name='ENTRY TICKET',
            description=f'Main entry for {event.name}',
            start_time=start_time,
            end_time=end_time,
            is_active=True
        )
        return [sub_event]


class CreateSubEventView(generics.CreateAPIView):
    """Admin: Create sub-event"""
    permission_classes = [IsAdmin]
    queryset = SubEvent.objects.all()
    serializer_class = SubEventSerializer


class SubEventListView(generics.ListAPIView):
    """Admin: List sub-events for an event"""
    permission_classes = [IsAdmin]
    serializer_class = SubEventSerializer

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        if event_id:
            return SubEvent.objects.filter(event_id=event_id)
        return SubEvent.objects.all()


class CreateEntryTypeView(generics.CreateAPIView):
    """Admin: Create entry type"""
    permission_classes = [IsAdmin]
    queryset = EntryType.objects.all()
    serializer_class = EntryTypeSerializer


class AdminEntryTypesView(generics.ListAPIView):
    """Admin: List entry types for a sub-event (including inactive)"""
    permission_classes = [IsAdmin]
    serializer_class = EntryTypeSerializer

    def get_queryset(self):
        sub_event_id = self.kwargs.get('sub_event_id')
        return EntryType.objects.filter(sub_event_id=sub_event_id)


class EntryTypeDetailView(generics.RetrieveAPIView):
    """Admin: Get single entry type details"""
    permission_classes = [IsAdmin]
    serializer_class = EntryTypeSerializer
    queryset = EntryType.objects.all()
    lookup_field = 'id'


class UpdateEntryTypeView(APIView):
    """Admin: Update entry type with conditional editing based on ticket generation"""
    permission_classes = [IsAdmin]
    
    @transaction.atomic
    def put(self, request, entry_type_id):
        try:
            entry_type = EntryType.objects.get(id=entry_type_id)
        except EntryType.DoesNotExist:
            return Response({'error': 'Entry type not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if tickets exist for this entry type
        tickets_count = Ticket.objects.filter(entry_type=entry_type).count()
        has_generated_tickets = tickets_count > 0
        
        if has_generated_tickets:
            # RESTRICTED EDITING - Only safe fields
            return self._handle_restricted_edit(entry_type, request.data, tickets_count)
        else:
            # FULL EDITING - All fields allowed
            return self._handle_full_edit(entry_type, request.data)
    
    def _handle_restricted_edit(self, entry_type, data, tickets_count):
        """Handle editing for entry types with existing tickets"""
        
        # Define allowed fields for entry types with tickets
        ALLOWED_FIELDS = [
            'description',  # Safe to update description
            'is_active'     # Safe to deactivate/activate
        ]
        
        # Check for restricted fields
        restricted_fields = []
        for field in data.keys():
            if field not in ALLOWED_FIELDS:
                restricted_fields.append(field)
        
        if restricted_fields:
            return Response({
                'error': 'Cannot edit these fields for entry type with existing tickets',
                'details': {
                    'tickets_generated': tickets_count,
                    'restricted_fields': restricted_fields,
                    'allowed_fields': ALLOWED_FIELDS,
                    'reason': 'Entry type has generated tickets - only safe fields can be edited to preserve historical data'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update only allowed fields
        updated_fields = []
        
        if 'description' in data:
            entry_type.description = data['description']
            updated_fields.append('description')
        
        if 'is_active' in data:
            entry_type.is_active = data['is_active']
            updated_fields.append('is_active')
        
        entry_type.save()
        
        return Response({
            'message': 'Entry type updated successfully (restricted mode)',
            'note': f'Limited editing due to {tickets_count} generated tickets',
            'updated_fields': updated_fields,
            'data': EntryTypeSerializer(entry_type).data
        })
    
    def _handle_full_edit(self, entry_type, data):
        """Handle full editing for entry types with no tickets"""
        
        # Validate all fields
        validation_errors = self._validate_full_edit(entry_type, data)
        if validation_errors:
            return Response({'errors': validation_errors}, status=status.HTTP_400_BAD_REQUEST)
        
        updated_fields = []
        
        # Update all allowed fields
        editable_fields = ['name', 'price', 'description', 'is_active']
        for field in editable_fields:
            if field in data:
                setattr(entry_type, field, data[field])
                updated_fields.append(field)
        
        entry_type.save()
        
        return Response({
            'message': 'Entry type updated successfully (full edit mode)',
            'note': 'All fields editable - no tickets generated yet',
            'updated_fields': updated_fields,
            'data': EntryTypeSerializer(entry_type).data
        })
    
    def _validate_full_edit(self, entry_type, data):
        """Validate full edit data"""
        errors = {}
        
        # Name uniqueness validation (within same sub-event)
        if 'name' in data:
            if EntryType.objects.filter(
                sub_event=entry_type.sub_event, 
                name=data['name']
            ).exclude(id=entry_type.id).exists():
                errors['name'] = 'Entry type name already exists in this sub-event'
        
        # Price validation
        if 'price' in data:
            try:
                price = float(data['price'])
                if price < 0:
                    errors['price'] = 'Price cannot be negative'
            except (ValueError, TypeError):
                errors['price'] = 'Invalid price format'
        
        # Boolean validation for is_active
        if 'is_active' in data and not isinstance(data['is_active'], bool):
            errors['is_active'] = 'is_active must be a boolean value'
        
        return errors


class DeleteEntryTypeView(APIView):
    """Admin: Smart delete entry type with validation"""
    permission_classes = [IsAdmin]
    
    def delete(self, request, entry_type_id):
        try:
            entry_type = EntryType.objects.get(id=entry_type_id)
        except EntryType.DoesNotExist:
            return Response({'error': 'Entry type not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if tickets exist for this entry type
        tickets_count = Ticket.objects.filter(entry_type=entry_type).count()
        
        # Store info for response
        entry_type_name = entry_type.name
        sub_event_name = entry_type.sub_event.name
        event_name = entry_type.sub_event.event.name
        
        if tickets_count > 0:
            # SOFT DELETE - preserve historical data
            entry_type.is_active = False
            entry_type.save()
            
            return Response({
                'message': f'Entry type "{entry_type_name}" deactivated successfully',
                'action': 'soft_delete',
                'details': {
                    'entry_type': entry_type_name,
                    'sub_event': sub_event_name,
                    'event': event_name,
                    'tickets_preserved': tickets_count,
                    'note': 'Entry type deactivated to preserve ticket history. It will not appear in staff lists but existing tickets remain intact.'
                }
            })
        else:
            # HARD DELETE - safe to remove completely
            entry_type.delete()
            
            return Response({
                'message': f'Entry type "{entry_type_name}" deleted permanently',
                'action': 'hard_delete',
                'details': {
                    'entry_type': entry_type_name,
                    'sub_event': sub_event_name,
                    'event': event_name,
                    'note': 'Entry type deleted completely as no tickets were generated for it.'
                }
            })


class ConfigureTicketView(APIView):
    """Admin: Configure ticket customization"""
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = TicketCustomizationSerializer(data=request.data)
        if serializer.is_valid():
            # Check if customization already exists for event
            event_id = serializer.validated_data['event'].id
            existing = TicketCustomization.objects.filter(event_id=event_id).first()
            
            if existing:
                # Update existing
                for key, value in serializer.validated_data.items():
                    setattr(existing, key, value)
                existing.save()
                return Response({
                    'message': 'Ticket customization updated',
                    'data': TicketCustomizationSerializer(existing).data
                })
            else:
                # Create new
                customization = serializer.save()
                return Response({
                    'message': 'Ticket customization created',
                    'data': TicketCustomizationSerializer(customization).data
                }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateEventView(APIView):
    """Admin: Update event with validation and optional sub-event selection"""
    permission_classes = [IsAdmin]

    @transaction.atomic
    def put(self, request, event_id):
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Extract sub-events from request data (optional - backward compatible)
        event_data = request.data.copy()
        selected_sub_events = event_data.pop('selected_sub_events', None)
        
        serializer = EventSerializer(event, data=event_data, partial=True)
        if serializer.is_valid():
            # Check if dates are being changed
            new_start_date = serializer.validated_data.get('start_date', event.start_date)
            new_end_date = serializer.validated_data.get('end_date', event.end_date)
            
            # Validate business rules (including sub-event changes if provided)
            validation_result = self._validate_event_changes(event, new_start_date, new_end_date, selected_sub_events)
            if not validation_result['valid']:
                return Response({'error': validation_result['message']}, status=status.HTTP_400_BAD_REQUEST)
            
            # Save the event
            updated_event = serializer.save()
            
            # Update sub-events if dates changed
            if new_start_date != event.start_date or new_end_date != event.end_date:
                self._update_sub_events_dates(updated_event, new_start_date, new_end_date)
            
            # Update sub-events selection if provided
            updated_sub_events = None
            if selected_sub_events is not None:
                updated_sub_events = self._update_sub_events_selection(updated_event, selected_sub_events, new_start_date, new_end_date)
            
            response_data = {
                'message': 'Event updated successfully',
                'data': EventSerializer(updated_event).data,
                'warnings': validation_result.get('warnings', [])
            }
            
            # Include sub-events in response if they were updated
            if updated_sub_events is not None:
                response_data['sub_events'] = SubEventSerializer(updated_sub_events, many=True).data
            
            return Response(response_data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _validate_event_changes(self, event, new_start_date, new_end_date, selected_sub_events=None):
        """Validate if event and sub-event changes are safe"""
        warnings = []
        
        # Check if tickets already generated
        ticket_count = Ticket.objects.filter(event=event).count()
        if ticket_count > 0:
            warnings.append(f'{ticket_count} tickets already generated for this event')
        
        # Check sub-events timing conflicts (only if not updating sub-events)
        if selected_sub_events is None:
            sub_events = SubEvent.objects.filter(event=event)
            conflicting_sub_events = []
            
            for sub_event in sub_events:
                sub_start_date = sub_event.start_time.date()
                sub_end_date = sub_event.end_time.date()
                
                if sub_start_date < new_start_date or sub_end_date > new_end_date:
                    conflicting_sub_events.append(sub_event.name)
            
            if conflicting_sub_events:
                warnings.append(f'Sub-events outside new date range: {", ".join(conflicting_sub_events)}')
        
        # Check staff assignments and tickets for sub-events being removed
        if selected_sub_events is not None:
            current_sub_events = set(SubEvent.objects.filter(event=event).values_list('name', flat=True))
            selected_set = set(selected_sub_events)
            
            # Sub-events being removed
            removed_sub_events = current_sub_events - selected_set
            
            if removed_sub_events:
                # Check for tickets in removed sub-events
                removed_tickets = Ticket.objects.filter(
                    event=event,
                    sub_event__name__in=removed_sub_events
                ).count()
                
                if removed_tickets > 0:
                    return {
                        'valid': False,
                        'message': f'Cannot remove sub-events with existing tickets. {removed_tickets} tickets found in: {", ".join(removed_sub_events)}'
                    }
                
                # Check for staff assignments in removed sub-events
                assigned_staff = StaffProfile.objects.filter(
                    assigned_sub_events__event=event,
                    assigned_sub_events__name__in=removed_sub_events
                ).distinct().count()
                
                if assigned_staff > 0:
                    warnings.append(f'{assigned_staff} staff members assigned to sub-events being removed: {", ".join(removed_sub_events)}')
                
                warnings.append(f'Sub-events will be removed: {", ".join(removed_sub_events)}')
            
            # Sub-events being added
            added_sub_events = selected_set - current_sub_events
            if added_sub_events:
                warnings.append(f'New sub-events will be added: {", ".join(added_sub_events)}')
        
        # Check staff assignments (general)
        assigned_staff_count = StaffProfile.objects.filter(
            assigned_sub_events__event=event
        ).distinct().count()
        
        if assigned_staff_count > 0 and selected_sub_events is None:
            warnings.append(f'{assigned_staff_count} staff members assigned to this event\'s sub-events')
        
        return {
            'valid': True,
            'warnings': warnings
        }
    
    def _update_sub_events_dates(self, event, new_start_date, new_end_date):
        """Update sub-events to fit within new event dates"""
        from datetime import datetime, time
        
        sub_events = SubEvent.objects.filter(event=event)
        
        for sub_event in sub_events:
            # Adjust sub-event dates to fit within event dates
            start_time = datetime.combine(new_start_date, time(9, 0))
            end_time = datetime.combine(new_end_date, time(23, 59))
            
            # Keep original time if within new range, otherwise adjust
            if sub_event.start_time.date() < new_start_date:
                sub_event.start_time = start_time
            if sub_event.end_time.date() > new_end_date:
                sub_event.end_time = end_time
            
            sub_event.save()
    
    def _update_sub_events_selection(self, event, selected_sub_events, start_date, end_date):
        """Update sub-events based on selection"""
        from datetime import datetime, time
        
        # Get current sub-events
        current_sub_events = SubEvent.objects.filter(event=event)
        current_names = set(current_sub_events.values_list('name', flat=True))
        selected_set = set(selected_sub_events)
        
        # Remove sub-events not in selection (already validated for tickets/staff)
        removed_names = current_names - selected_set
        if removed_names:
            # Remove staff assignments first
            removed_sub_events = current_sub_events.filter(name__in=removed_names)
            for sub_event in removed_sub_events:
                sub_event.assigned_staff.clear()
            
            # Delete removed sub-events
            current_sub_events.filter(name__in=removed_names).delete()
        
        # Add new sub-events
        added_names = selected_set - current_names
        start_time = datetime.combine(start_date, time(9, 0))
        end_time = datetime.combine(end_date, time(23, 59))
        
        for name in added_names:
            SubEvent.objects.create(
                event=event,
                name=name,
                description=f'{name} for {event.name}',
                start_time=start_time,
                end_time=end_time,
                is_active=True
            )
        
        # Return updated sub-events
        return SubEvent.objects.filter(event=event).order_by('created_at')
    
    def _validate_date_change(self, event, new_start_date, new_end_date):
        """Legacy method - kept for backward compatibility"""
        return self._validate_event_changes(event, new_start_date, new_end_date)


class EventListView(generics.ListAPIView):
    """Admin: List all events"""
    permission_classes = [IsAdmin]
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class TicketReportPagination(PageNumberPagination):
    page_size = 100  # Default 100 tickets per page
    page_size_query_param = 'page_size'
    max_page_size = 500  # Maximum 500 tickets per page


class TicketsReportView(APIView):
    """Admin: Tickets report with pagination support"""
    permission_classes = [IsAdmin]

    def get(self, request):
        event_id = request.query_params.get('event_id')
        
        # Optimize query with ordering and select_related
        queryset = Ticket.objects.select_related(
            'event', 'sub_event', 'entry_type', 'staff'
        ).order_by('-created_at')
        
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        
        # Check if pagination is requested (page parameter exists)
        if 'page' in request.query_params:
            # Use pagination
            paginator = TicketReportPagination()
            page = paginator.paginate_queryset(queryset, request)
            
            if page is not None:
                tickets = TicketSerializer(page, many=True).data
                return paginator.get_paginated_response({
                    'total_tickets': queryset.count(),
                    'tickets': tickets
                })
        
        # Backward compatibility - no pagination requested
        total_count = queryset.count()
        
        # Safety check for large datasets
        if total_count > 1000:
            return Response({
                'error': f'Dataset too large ({total_count} tickets). Please use pagination.',
                'total_tickets': total_count,
                'suggestion': 'Add ?page=1&page_size=100 to your request for paginated results',
                'example_url': f'{request.build_absolute_uri()}?page=1&page_size=100'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Small datasets - return as before
        tickets = TicketSerializer(queryset, many=True).data
        
        return Response({
            'total_tickets': total_count,
            'tickets': tickets
        })


class RevenueReportView(APIView):
    """Admin: Revenue report"""
    permission_classes = [IsAdmin]

    def get(self, request):
        event_id = request.query_params.get('event_id')
        
        queryset = Ticket.objects.all()
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        
        # Calculate revenue by event
        revenue_by_event = queryset.values('event__name', 'event__code').annotate(
            total_revenue=Sum('price'),
            ticket_count=Count('id')
        )
        
        total_revenue = queryset.aggregate(total=Sum('price'))['total'] or 0
        
        return Response({
            'total_revenue': total_revenue,
            'revenue_by_event': list(revenue_by_event)
        })


class StaffSummaryReportView(APIView):
    """Admin: Staff summary report"""
    permission_classes = [IsAdmin]

    def get(self, request):
        staff_id = request.query_params.get('staff_id')
        
        queryset = StaffProfile.objects.all()
        if staff_id:
            queryset = queryset.filter(id=staff_id)
        
        summary = []
        for staff in queryset:
            tickets_generated = Ticket.objects.filter(staff=staff.user).count()
            total_revenue = Ticket.objects.filter(staff=staff.user).aggregate(
                total=Sum('price')
            )['total'] or 0
            
            summary.append({
                'staff_id': staff.id,
                'username': staff.user.username,
                'staff_code': staff.get_staff_code(),
                'role': staff.role,
                'range_start': staff.range_start,
                'range_end': staff.range_end,
                'current_counter': staff.current_counter,
                'tickets_generated': tickets_generated,
                'total_revenue': total_revenue,
                'remaining_tickets': staff.range_end - (staff.range_start + staff.current_counter) + 1
            })
        
        return Response({'staff_summary': summary})


class DeleteEventView(APIView):
    """Admin: Delete event and all related data"""
    permission_classes = [IsAdmin]

    @transaction.atomic
    def delete(self, request, event_id):
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get counts before deletion (for response)
        ticket_count = event.tickets.count()
        sub_event_count = event.sub_events.count()
        entry_type_count = sum(se.entry_types.count() for se in event.sub_events.all())
        
        # Get event name before deletion
        event_name = event.name
        event_code = event.code
        
        # Delete event (CASCADE will handle related data)
        event.delete()
        
        return Response({
            'message': f'Event "{event_name}" ({event_code}) deleted successfully',
            'deleted_data': {
                'event_name': event_name,
                'event_code': event_code,
                'sub_events': sub_event_count,
                'entry_types': entry_type_count,
                'tickets': ticket_count
            }
        })


# ==================== MASTER DATA VIEWS ====================

class SubEventMasterListView(generics.ListAPIView):
    """Admin: List all master sub-events"""
    permission_classes = [IsAdmin]
    serializer_class = SubEventMasterSerializer
    queryset = SubEventMaster.objects.all()


class SubEventMasterCreateView(generics.CreateAPIView):
    """Admin: Create new master sub-event"""
    permission_classes = [IsAdmin]
    serializer_class = SubEventMasterSerializer
    queryset = SubEventMaster.objects.all()


class SubEventMasterUpdateView(generics.UpdateAPIView):
    """Admin: Update master sub-event"""
    permission_classes = [IsAdmin]
    serializer_class = SubEventMasterSerializer
    queryset = SubEventMaster.objects.all()
    lookup_field = 'id'


class SubEventMasterDeleteView(APIView):
    """Admin: Delete master sub-event with validation"""
    permission_classes = [IsAdmin]
    
    def delete(self, request, id):
        try:
            master_sub_event = SubEventMaster.objects.get(id=id)
        except SubEventMaster.DoesNotExist:
            return Response({'error': 'Master sub-event not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if it can be safely deleted
        if not master_sub_event.can_delete():
            usage_count = SubEvent.objects.filter(name=master_sub_event.name).count()
            return Response({
                'error': 'Cannot delete master sub-event',
                'reason': f'This sub-event is currently used in {usage_count} event(s)',
                'suggestion': 'Deactivate instead of deleting, or remove from all events first'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Safe to delete
        name = master_sub_event.name
        master_sub_event.delete()
        
        return Response({
            'message': f'Master sub-event "{name}" deleted successfully'
        })


# ==================== STAFF VIEWS ====================

class StaffEventsView(generics.ListAPIView):
    """Staff: View events from assigned sub-events"""
    permission_classes = [IsStaff]
    serializer_class = EventSerializer

    def get_queryset(self):
        staff_profile = self.request.user.staff_profile
        # Get unique events from assigned sub-events
        sub_events = staff_profile.assigned_sub_events.all()
        event_ids = sub_events.values_list('event_id', flat=True).distinct()
        return Event.objects.filter(id__in=event_ids)


class StaffSubEventsView(generics.ListAPIView):
    """Staff: View all assigned sub-events"""
    permission_classes = [IsStaff]
    serializer_class = SubEventSerializer

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        staff_profile = self.request.user.staff_profile
        
        # If event_id is 0, return all assigned sub-events
        if event_id == 0:
            return staff_profile.assigned_sub_events.filter(is_active=True)
        
        # Return only assigned sub-events for this event
        return staff_profile.assigned_sub_events.filter(event_id=event_id, is_active=True)


class StaffEntryTypesView(generics.ListAPIView):
    """Staff: View entry types for a sub-event"""
    permission_classes = [IsStaff]
    serializer_class = EntryTypeSerializer

    def get_queryset(self):
        sub_event_id = self.kwargs.get('sub_event_id')
        return EntryType.objects.filter(sub_event_id=sub_event_id, is_active=True)


class GenerateTicketView(APIView):
    """Staff: Generate ticket(s) with multiple entry types"""
    permission_classes = [IsStaff]

    def post(self, request):
        serializer = GenerateTicketSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.validated_data['event']
            sub_event = serializer.validated_data['sub_event']
            validated_tickets = serializer.validated_data['validated_tickets']
            
            try:
                # Generate tickets using service
                tickets = TicketService.generate_tickets(
                    user=request.user,
                    event=event,
                    sub_event=sub_event,
                    tickets_data=validated_tickets
                )
                
                # Get print data for all tickets
                tickets_data = [TicketService.get_ticket_print_data(ticket) for ticket in tickets]
                
                # Calculate total quantity
                total_quantity = len(tickets)
                
                return Response({
                    'message': f'{total_quantity} ticket(s) generated successfully',
                    'group_id': tickets[0].group_id,
                    'total_quantity': total_quantity,
                    'tickets': tickets_data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyTicketView(APIView):
    """Staff: Verify if ticket exists"""
    permission_classes = [IsStaff]
    
    def post(self, request):
        ticket_id = request.data.get('ticket_id')
        
        if not ticket_id:
            return Response({'error': 'ticket_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check exact match first
        exists = Ticket.objects.filter(ticket_id=ticket_id).exists()
        
        if not exists:
            # Check if input matches the pattern: staffcode-eventcode-subeventcode-sequence
            # Input: U3-WF-WAY-5358
            # DB: U3-WF-WAY-5358-1772693873163-2
            exists = Ticket.objects.filter(ticket_id__startswith=ticket_id + '-').exists()
        
        # Debug: Get actual ticket IDs for troubleshooting
        debug_tickets = list(Ticket.objects.values_list('ticket_id', flat=True)[:5])
        
        return Response({
            'status': 'verified' if exists else 'unverified',
            'debug_input': ticket_id,
            'debug_search_pattern': ticket_id + '-',
            'debug_sample_tickets': debug_tickets
        })


# ==================== AUTH VIEWS ====================

class LoginView(TokenObtainPairView):
    """Login endpoint for all users"""
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Get user info
            username = request.data.get('username')
            user = User.objects.get(username=username)
            
            if hasattr(user, 'staff_profile'):
                response.data['user'] = {
                    'id': user.id,
                    'username': user.username,
                    'role': user.staff_profile.role,
                    'staff_code': user.staff_profile.get_staff_code(),
                    'range_start': user.staff_profile.range_start,
                    'range_end': user.staff_profile.range_end,
                    'current_counter': user.staff_profile.current_counter
                }
            else:
                response.data['user'] = {
                    'id': user.id,
                    'username': user.username,
                    'role': 'superuser',
                    'staff_code': None
                }
        
        return response


# //