from django.urls import path
from .views import (
    # Admin views
    CreateStaffView, StaffListView, UpdateStaffView, DeleteStaffView, AssignEventsToStaffView, PredefinedSubEventsView, CreateEventView, UpdateEventView, CreateSubEventView,
    SubEventListView, CreateEntryTypeView, AdminEntryTypesView, EntryTypeDetailView, UpdateEntryTypeView, DeleteEntryTypeView, ConfigureTicketView, EventListView, DeleteEventView,
    TicketsReportView, RevenueReportView, StaffSummaryReportView, BulkDeleteTicketsView,
    # Master Data views
    SubEventMasterListView, SubEventMasterCreateView, SubEventMasterUpdateView, SubEventMasterDeleteView,
    # Staff views
    StaffEventsView, StaffSubEventsView, StaffEntryTypesView, GenerateTicketView, VerifyTicketView,
    # Auth views
    LoginView
)

urlpatterns = [
    # Auth
    path('login/', LoginView.as_view(), name='login'),
    
    # Admin endpoints
    path('admin/predefined-sub-events/', PredefinedSubEventsView.as_view(), name='admin-predefined-sub-events'),
    path('admin/create-staff/', CreateStaffView.as_view(), name='admin-create-staff'),
    path('admin/staff-list/', StaffListView.as_view(), name='admin-staff-list'),
    path('admin/update-staff/<int:staff_id>/', UpdateStaffView.as_view(), name='admin-update-staff'),
    path('admin/delete-staff/<int:staff_id>/', DeleteStaffView.as_view(), name='admin-delete-staff'),
    path('admin/assign-events/', AssignEventsToStaffView.as_view(), name='admin-assign-sub-events'),
    path('admin/create-event/', CreateEventView.as_view(), name='admin-create-event'),
    path('admin/update-event/<int:event_id>/', UpdateEventView.as_view(), name='admin-update-event'),
    path('admin/delete-event/<int:event_id>/', DeleteEventView.as_view(), name='admin-delete-event'),
    path('admin/create-sub-event/', CreateSubEventView.as_view(), name='admin-create-sub-event'),
    path('admin/sub-events/<int:event_id>/', SubEventListView.as_view(), name='admin-sub-event-list'),
    path('admin/create-entry-type/', CreateEntryTypeView.as_view(), name='admin-create-entry-type'),
    path('admin/entry-types/<int:sub_event_id>/', AdminEntryTypesView.as_view(), name='admin-entry-types'),
    path('admin/entry-type/<int:id>/', EntryTypeDetailView.as_view(), name='admin-entry-type-detail'),
    path('admin/entry-type/<int:entry_type_id>/update/', UpdateEntryTypeView.as_view(), name='admin-update-entry-type'),
    path('admin/entry-type/<int:entry_type_id>/delete/', DeleteEntryTypeView.as_view(), name='admin-delete-entry-type'),
    path('admin/configure-ticket/', ConfigureTicketView.as_view(), name='admin-configure-ticket'),
    path('admin/event-list/', EventListView.as_view(), name='admin-event-list'),
    path('admin/reports/tickets/', TicketsReportView.as_view(), name='admin-tickets-report'),
    path('admin/reports/revenue/', RevenueReportView.as_view(), name='admin-revenue-report'),
    path('admin/reports/staff-summary/', StaffSummaryReportView.as_view(), name='admin-staff-summary'),
    path('admin/tickets/bulk-delete/', BulkDeleteTicketsView.as_view(), name='admin-bulk-delete-tickets'),
    
    # Master Data endpoints
    path('admin/master-sub-events/', SubEventMasterListView.as_view(), name='admin-master-sub-events-list'),
    path('admin/master-sub-events/create/', SubEventMasterCreateView.as_view(), name='admin-master-sub-events-create'),
    path('admin/master-sub-events/<int:id>/', SubEventMasterUpdateView.as_view(), name='admin-master-sub-events-update'),
    path('admin/master-sub-events/<int:id>/delete/', SubEventMasterDeleteView.as_view(), name='admin-master-sub-events-delete'),
    
    # Staff endpoints
    path('staff/events/', StaffEventsView.as_view(), name='staff-events'),
    path('staff/sub-events/<int:event_id>/', StaffSubEventsView.as_view(), name='staff-sub-events'),
    path('staff/entry-types/<int:sub_event_id>/', StaffEntryTypesView.as_view(), name='staff-entry-types'),
    path('staff/generate-ticket/', GenerateTicketView.as_view(), name='staff-generate-ticket'),
    path('staff/verify-ticket/', VerifyTicketView.as_view(), name='staff-verify-ticket'),
]
