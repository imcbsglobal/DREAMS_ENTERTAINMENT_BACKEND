from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from .models import Ticket, StaffProfile, SubEvent


class TicketService:
    """
    Service class for ticket generation logic
    """
    
    @staticmethod
    @transaction.atomic
    def generate_tickets(user, event, sub_event, tickets_data):
        """
        Generate multiple tickets with different entry types in one group
        
        Args:
            user: User object (staff)
            event: Event object
            sub_event: SubEvent object
            tickets_data: List of dicts with 'entry_type' and 'quantity'
            
        Returns:
            List of Ticket objects
            
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
        
        # Calculate total quantity
        total_quantity = sum(item['quantity'] for item in tickets_data)
        
        # Calculate next sequence number
        next_sequence = staff_profile.range_start + staff_profile.current_counter
        
        # Check if within range for all tickets
        if next_sequence + total_quantity - 1 > staff_profile.range_end:
            raise ValidationError(
                f"Not enough tickets in range. Available: {staff_profile.range_end - next_sequence + 1}, Requested: {total_quantity}"
            )
        
        # Generate codes
        staff_code = staff_profile.get_staff_code()
        event_code = event.code
        sub_event_code = sub_event.code
        
        # Generate ONE group_id with timestamp for uniqueness
        timestamp = int(timezone.now().timestamp() * 1000)  # milliseconds
        group_id = f"{staff_code}-{event_code}-{sub_event_code}-{next_sequence}-{timestamp}"
        
        # Create tickets
        tickets = []
        ticket_index = 1
        
        for ticket_item in tickets_data:
            entry_type = ticket_item['entry_type']
            quantity = ticket_item['quantity']
            
            for i in range(quantity):
                if total_quantity == 1:
                    # Single ticket: ticket_id = group_id
                    ticket_id = group_id
                else:
                    # Multiple tickets: ticket_id = group_id-{index}
                    ticket_id = f"{group_id}-{ticket_index}"
                
                # Check for duplicate ticket_id
                if Ticket.objects.filter(ticket_id=ticket_id).exists():
                    raise ValidationError("Ticket ID conflict. Please try again.")
                
                # Create ticket
                ticket = Ticket.objects.create(
                    ticket_id=ticket_id,
                    group_id=group_id,
                    quantity_in_group=total_quantity,
                    event=event,
                    sub_event=sub_event,
                    entry_type=entry_type,
                    staff=user,
                    sequence_number=next_sequence + ticket_index - 1,
                    price=entry_type.price
                )
                tickets.append(ticket)
                ticket_index += 1
        
        # Increment counter by total quantity
        staff_profile.current_counter += total_quantity
        staff_profile.save()
        
        return tickets
    
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
            'group_id': ticket.group_id,
            'quantity_in_group': ticket.quantity_in_group,
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
