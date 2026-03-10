from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Sum, Count, Q
from django.utils import timezone
from .models import Event, SubEvent, EntryType, StaffProfile, TicketCustomization, Ticket
from .serializers import (
    EventSerializer, SubEventSerializer, EntryTypeSerializer, StaffProfileSerializer,
    CreateStaffSerializer, TicketCustomizationSerializer, TicketSerializer,
    GenerateTicketSerializer, TicketPrintSerializer
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


class StaffListView(generics.ListAPIView):
    """Admin: List all staff"""
    permission_classes = [IsAdmin]
    queryset = StaffProfile.objects.all()
    serializer_class = StaffProfileSerializer


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


class CreateEventView(generics.CreateAPIView):
    """Admin: Create event"""
    permission_classes = [IsAdmin]
    queryset = Event.objects.all()
    serializer_class = EventSerializer


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


class EventListView(generics.ListAPIView):
    """Admin: List all events"""
    permission_classes = [IsAdmin]
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class TicketsReportView(APIView):
    """Admin: Tickets report"""
    permission_classes = [IsAdmin]

    def get(self, request):
        event_id = request.query_params.get('event_id')
        
        queryset = Ticket.objects.all()
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        
        tickets = TicketSerializer(queryset, many=True).data
        
        return Response({
            'total_tickets': queryset.count(),
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