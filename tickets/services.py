from django.db import transaction
from rest_framework.exceptions import ValidationError
from .models import Ticket, StaffProfile, SubEvent


class TicketService:
    """
    Service class for ticket generation logic
    """
    
    @staticmethod
    @transaction.atomic
    def generate_ticket(user, event, sub_event, entry_type):
        """
        Generate a ticket with proper validation and atomic transaction
        
        Args:
            user: User object (staff)
            event: Event object
            sub_event: SubEvent object
            entry_type: EntryType object
            
        Returns:
            Ticket object
            
        Raises:
            ValidationError: If validation fails
        """
        # Get staff profile with select_for_update to prevent race conditions
        try:
            staff_profile = StaffProfile.objects.select_for_update().get(user=user)
        except StaffProfile.DoesNotExist:
            raise ValidationError("Staff profile not found")
        
        # Validate role
        if staff_profile.role != 'staff':
            raise ValidationError("Only staff members can generate tickets")
        
        # Check if sub-event is assigned to this staff
        if not staff_profile.assigned_sub_events.filter(id=sub_event.id).exists():
            raise ValidationError("This sub-event is not assigned to you")
        
        # Calculate next sequence number
        next_sequence = staff_profile.range_start + staff_profile.current_counter
        
        # Check if within range
        if next_sequence > staff_profile.range_end:
            raise ValidationError(
                f"Ticket range exhausted. Current range: {staff_profile.range_start}-{staff_profile.range_end}"
            )
        
        # Generate ticket ID: [STAFFCODE]-[EVENTCODE]-[SUBEVENTCODE]-[SEQUENCE]
        staff_code = staff_profile.get_staff_code()
        event_code = event.code
        sub_event_code = sub_event.code
        ticket_id = f"{staff_code}-{event_code}-{sub_event_code}-{next_sequence}"
        
        # Check for duplicate ticket_id (should not happen with proper locking)
        if Ticket.objects.filter(ticket_id=ticket_id).exists():
            raise ValidationError("Ticket ID conflict. Please try again.")
        
        # Create ticket
        ticket = Ticket.objects.create(
            ticket_id=ticket_id,
            event=event,
            sub_event=sub_event,
            entry_type=entry_type,
            staff=user,
            sequence_number=next_sequence,
            price=entry_type.price
        )
        
        # Increment counter
        staff_profile.current_counter += 1
        staff_profile.save()
        
        return ticket
    
    @staticmethod
    def get_ticket_print_data(ticket):
        """
        Get formatted ticket data for printing
        
        Args:
            ticket: Ticket object
            
        Returns:
            dict: Formatted ticket data
        """
        event = ticket.event
        sub_event = ticket.sub_event
        customization = getattr(event, 'customization', None)
        
        data = {
            'ticket_id': ticket.ticket_id,
            'event_name': event.name if not customization or customization.show_event_name else '',
            'sub_event_name': sub_event.name,
            'place': event.place if not customization or customization.show_place else '',
            'entry_type': ticket.entry_type.name if not customization or customization.show_entry_type else '',
            'price': ticket.price if not customization or customization.show_price else 0,
            'header_text': customization.header_text if customization else '',
            'footer_text': customization.footer_text if customization else '',
            'created_at': ticket.created_at,
            'sequence_number': ticket.sequence_number,
        }
        
        return data
