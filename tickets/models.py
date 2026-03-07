from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class Event(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True, editable=False)
    place = models.CharField(max_length=200)
    address = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            # Generate code from first 2 uppercase letters
            words = self.name.split()
            if len(words) >= 2:
                self.code = (words[0][0] + words[1][0]).upper()
            else:
                self.code = self.name[:2].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        ordering = ['-created_at']


@receiver(post_save, sender=Event)
def create_default_subevent(sender, instance, created, **kwargs):
    """Automatically create a default sub-event with same name as Event when Event is created"""
    if created:
        from django.utils import timezone
        from datetime import datetime, time
        
        # Create start_time and end_time from event dates
        start_time = datetime.combine(instance.start_date, time(9, 0))  # 9 AM
        end_time = datetime.combine(instance.end_date, time(23, 59))    # 11:59 PM
        
        SubEvent.objects.create(
            event=instance,
            name=instance.name,
            description=f'Main entry for {instance.name}',
            start_time=start_time,
            end_time=end_time,
            is_active=True
        )


class SubEvent(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='sub_events')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, editable=False)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.name[:3].upper().replace(' ', '')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.event.name} - {self.name}"

    class Meta:
        unique_together = ['event', 'code']
        ordering = ['start_time']


class EntryType(models.Model):
    sub_event = models.ForeignKey(SubEvent, on_delete=models.CASCADE, related_name='entry_types')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.sub_event.event.name} - {self.sub_event.name} - {self.name}"

    class Meta:
        unique_together = ['sub_event', 'name']


class StaffProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')
    range_start = models.IntegerField(validators=[MinValueValidator(1)])
    range_end = models.IntegerField(validators=[MinValueValidator(1)])
    current_counter = models.IntegerField(default=0)
    assigned_sub_events = models.ManyToManyField(SubEvent, related_name='assigned_staff', blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    def get_staff_code(self):
        """Generate staff code from username (e.g., U1 from user1)"""
        return f"U{self.user.id}"

    class Meta:
        ordering = ['user__username']


class TicketCustomization(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='customization')
    header_text = models.CharField(max_length=500, blank=True)
    footer_text = models.CharField(max_length=500, blank=True)
    show_event_name = models.BooleanField(default=True)
    show_place = models.BooleanField(default=True)
    show_entry_type = models.BooleanField(default=True)
    show_price = models.BooleanField(default=True)
    printer_format = models.TextField(blank=True, help_text="Text layout template for printer")

    def __str__(self):
        return f"Customization for {self.event.name}"


class Ticket(models.Model):
    ticket_id = models.CharField(max_length=50, unique=True, db_index=True)
    group_id = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    quantity_in_group = models.IntegerField(default=1)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    sub_event = models.ForeignKey(SubEvent, on_delete=models.CASCADE, related_name='tickets')
    entry_type = models.ForeignKey(EntryType, on_delete=models.CASCADE, related_name='tickets')
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_tickets')
    sequence_number = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ticket_id

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ticket_id']),
            models.Index(fields=['event', 'created_at']),
            models.Index(fields=['sub_event', 'created_at']),
        ]
