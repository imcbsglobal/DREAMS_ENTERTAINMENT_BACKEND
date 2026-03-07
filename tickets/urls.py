from django.urls import path
from .views import (
    # Admin views
    CreateStaffView, StaffListView, AssignEventsToStaffView, CreateEventView, CreateSubEventView,
    SubEventListView, CreateEntryTypeView, ConfigureTicketView, EventListView, 
    TicketsReportView, RevenueReportView, StaffSummaryReportView,
    # Staff views
    StaffEventsView, StaffSubEventsView, StaffEntryTypesView, GenerateTicketView, VerifyTicketView,
    # Auth views
    LoginView
)

urlpatterns = [
    # Auth
    path('login/', LoginView.as_view(), name='login'),
    
    # Admin endpoints
    path('admin/create-staff/', CreateStaffView.as_view(), name='admin-create-staff'),
    path('admin/staff-list/', StaffListView.as_view(), name='admin-staff-list'),
    path('admin/assign-events/', AssignEventsToStaffView.as_view(), name='admin-assign-sub-events'),
    path('admin/create-event/', CreateEventView.as_view(), name='admin-create-event'),
    path('admin/create-sub-event/', CreateSubEventView.as_view(), name='admin-create-sub-event'),
    path('admin/sub-events/<int:event_id>/', SubEventListView.as_view(), name='admin-sub-event-list'),
    path('admin/create-entry-type/', CreateEntryTypeView.as_view(), name='admin-create-entry-type'),
    path('admin/configure-ticket/', ConfigureTicketView.as_view(), name='admin-configure-ticket'),
    path('admin/event-list/', EventListView.as_view(), name='admin-event-list'),
    path('admin/reports/tickets/', TicketsReportView.as_view(), name='admin-tickets-report'),
    path('admin/reports/revenue/', RevenueReportView.as_view(), name='admin-revenue-report'),
    path('admin/reports/staff-summary/', StaffSummaryReportView.as_view(), name='admin-staff-summary'),
    
    # Staff endpoints
    path('staff/events/', StaffEventsView.as_view(), name='staff-events'),
    path('staff/sub-events/<int:event_id>/', StaffSubEventsView.as_view(), name='staff-sub-events'),
    path('staff/entry-types/<int:sub_event_id>/', StaffEntryTypesView.as_view(), name='staff-entry-types'),
    path('staff/generate-ticket/', GenerateTicketView.as_view(), name='staff-generate-ticket'),
    path('staff/verify-ticket/', VerifyTicketView.as_view(), name='staff-verify-ticket'),
]
