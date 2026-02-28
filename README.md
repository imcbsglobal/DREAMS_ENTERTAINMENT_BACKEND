# Festival Ticket Management System - Backend API

A production-ready Django REST Framework backend for managing festival tickets with role-based access control.

## Tech Stack

- Django 4.2+
- Django REST Framework
- PostgreSQL
- JWT Authentication (djangorestframework-simplejwt)
- Python 3.8+

## Features

- **Role-Based Access Control**: Admin and Staff roles with custom permissions
- **JWT Authentication**: Secure token-based authentication
- **Ticket Generation**: Unique ticket ID generation with sequence management
- **Event Management**: Create and manage events with multiple entry types
- **Ticket Customization**: Configure ticket appearance per event
- **Reports**: Tickets, revenue, and staff summary reports
- **Transaction Safety**: Atomic operations for ticket generation

## Project Structure

```
festival_ticket_system/
├── festival_ticket_system/     # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── tickets/                    # Main app
│   ├── models.py              # Database models
│   ├── serializers.py         # DRF serializers
│   ├── views.py               # API views
│   ├── permissions.py         # Custom permissions
│   ├── services.py            # Business logic
│   ├── urls.py                # App URLs
│   └── admin.py               # Admin configuration
├── requirements.txt
└── manage.py
```

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Database

Update `festival_ticket_system/settings.py` with your PostgreSQL credentials:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'festival_tickets_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

For development, you can use SQLite by uncommenting the SQLite configuration in settings.py.

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

After creating superuser, create a StaffProfile for them:

```python
python manage.py shell

from django.contrib.auth.models import User
from tickets.models import StaffProfile

user = User.objects.get(username='your_superuser_username')
StaffProfile.objects.create(
    user=user,
    role='admin',
    range_start=1,
    range_end=1000
)
```

### 5. Run Server

```bash
python manage.py runserver
```

Server will run at: `http://localhost:8000`

## API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Authentication

All endpoints (except login) require JWT authentication.

**Headers:**
```
Authorization: Bearer <access_token>
```

---

## API Endpoints

### 1. Authentication

#### Login
```http
POST /api/login/
```

**Request:**
```json
{
    "username": "staff1",
    "password": "password123"
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
        "id": 2,
        "username": "staff1",
        "role": "staff",
        "staff_code": "U2"
    }
}
```

#### Refresh Token
```http
POST /api/token/refresh/
```

**Request:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## Admin APIs (Admin Only)

### 2. Create Staff

```http
POST /api/admin/create-staff/
```

**Request:**
```json
{
    "username": "staff1",
    "password": "password123",
    "email": "staff1@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "staff",
    "range_start": 5001,
    "range_end": 6000
}
```

**Response:**
```json
{
    "message": "Staff created successfully",
    "data": {
        "id": 2,
        "user": {
            "id": 2,
            "username": "staff1",
            "email": "staff1@example.com",
            "first_name": "John",
            "last_name": "Doe"
        },
        "role": "staff",
        "range_start": 5001,
        "range_end": 6000,
        "current_counter": 0,
        "staff_code": "U2"
    }
}
```

### 3. List Staff

```http
GET /api/admin/staff-list/
```

**Response:**
```json
[
    {
        "id": 2,
        "user": {
            "id": 2,
            "username": "staff1",
            "email": "staff1@example.com",
            "first_name": "John",
            "last_name": "Doe"
        },
        "role": "staff",
        "range_start": 5001,
        "range_end": 6000,
        "current_counter": 15,
        "staff_code": "U2"
    }
]
```

### 4. Create Event

```http
POST /api/admin/create-event/
```

**Request:**
```json
{
    "name": "Summer Festival",
    "place": "Central Park",
    "address": "123 Park Avenue, New York, NY",
    "start_date": "2024-06-01",
    "end_date": "2024-06-03"
}
```

**Response:**
```json
{
    "id": 1,
    "name": "Summer Festival",
    "code": "SF",
    "place": "Central Park",
    "address": "123 Park Avenue, New York, NY",
    "start_date": "2024-06-01",
    "end_date": "2024-06-03",
    "created_at": "2024-01-15T10:30:00Z"
}
```

### 5. Create Entry Type

```http
POST /api/admin/create-entry-type/
```

**Request:**
```json
{
    "event": 1,
    "name": "Adult",
    "price": "50.00",
    "description": "Adult entry ticket",
    "is_active": true
}
```

**Response:**
```json
{
    "id": 1,
    "event": 1,
    "name": "Adult",
    "price": "50.00",
    "description": "Adult entry ticket",
    "is_active": true
}
```

### 6. Configure Ticket Customization

```http
POST /api/admin/configure-ticket/
```

**Request:**
```json
{
    "event": 1,
    "header_text": "Welcome to Summer Festival 2024",
    "footer_text": "Thank you for your visit!",
    "show_event_name": true,
    "show_place": true,
    "show_entry_type": true,
    "show_price": true,
    "printer_format": "Header: {header}\nEvent: {event}\nPlace: {place}\nType: {type}\nPrice: ${price}\nFooter: {footer}"
}
```

**Response:**
```json
{
    "message": "Ticket customization created",
    "data": {
        "id": 1,
        "event": 1,
        "header_text": "Welcome to Summer Festival 2024",
        "footer_text": "Thank you for your visit!",
        "show_event_name": true,
        "show_place": true,
        "show_entry_type": true,
        "show_price": true,
        "printer_format": "Header: {header}\nEvent: {event}\nPlace: {place}\nType: {type}\nPrice: ${price}\nFooter: {footer}"
    }
}
```

### 7. List Events

```http
GET /api/admin/event-list/
```

### 8. Tickets Report

```http
GET /api/admin/reports/tickets/?event_id=1
```

**Response:**
```json
{
    "total_tickets": 150,
    "tickets": [
        {
            "id": 1,
            "ticket_id": "U2-SF-5001",
            "event": 1,
            "event_name": "Summer Festival",
            "entry_type": 1,
            "entry_type_name": "Adult",
            "staff": 2,
            "staff_username": "staff1",
            "sequence_number": 5001,
            "price": "50.00",
            "created_at": "2024-01-15T14:30:00Z"
        }
    ]
}
```

### 9. Revenue Report

```http
GET /api/admin/reports/revenue/?event_id=1
```

**Response:**
```json
{
    "total_revenue": "7500.00",
    "revenue_by_event": [
        {
            "event__name": "Summer Festival",
            "event__code": "SF",
            "total_revenue": "7500.00",
            "ticket_count": 150
        }
    ]
}
```

### 10. Staff Summary Report

```http
GET /api/admin/reports/staff-summary/?staff_id=2
```

**Response:**
```json
{
    "staff_summary": [
        {
            "staff_id": 2,
            "username": "staff1",
            "staff_code": "U2",
            "role": "staff",
            "range_start": 5001,
            "range_end": 6000,
            "current_counter": 15,
            "tickets_generated": 15,
            "total_revenue": "750.00",
            "remaining_tickets": 985
        }
    ]
}
```

---

## Staff APIs

### 11. View Events

```http
GET /api/staff/events/
```

**Response:**
```json
[
    {
        "id": 1,
        "name": "Summer Festival",
        "code": "SF",
        "place": "Central Park",
        "address": "123 Park Avenue, New York, NY",
        "start_date": "2024-06-01",
        "end_date": "2024-06-03",
        "created_at": "2024-01-15T10:30:00Z"
    }
]
```

### 12. View Entry Types

```http
GET /api/staff/entry-types/1/
```

**Response:**
```json
[
    {
        "id": 1,
        "event": 1,
        "name": "Adult",
        "price": "50.00",
        "description": "Adult entry ticket",
        "is_active": true
    },
    {
        "id": 2,
        "event": 1,
        "name": "Kids",
        "price": "25.00",
        "description": "Kids entry ticket",
        "is_active": true
    }
]
```

### 13. Generate Ticket

```http
POST /api/staff/generate-ticket/
```

**Request:**
```json
{
    "event_id": 1,
    "entry_type_id": 1
}
```

**Response:**
```json
{
    "message": "Ticket generated successfully",
    "ticket": {
        "ticket_id": "U2-SF-5001",
        "event_name": "Summer Festival",
        "place": "Central Park",
        "entry_type": "Adult",
        "price": "50.00",
        "header_text": "Welcome to Summer Festival 2024",
        "footer_text": "Thank you for your visit!",
        "created_at": "2024-01-15T14:30:00Z",
        "sequence_number": 5001
    }
}
```

---

## Ticket ID Format

Format: `[STAFFCODE]-[EVENTCODE]-[SEQUENCE]`

Example: `U2-SF-5001`

- **STAFFCODE**: U{user_id} (e.g., U2 for user with id=2)
- **EVENTCODE**: First 2 uppercase letters of event name (e.g., SF for "Summer Festival")
- **SEQUENCE**: Sequential number from staff's assigned range

---

## Security Features

1. **JWT Authentication**: Secure token-based authentication
2. **Role-Based Access Control**: Custom permission classes (IsAdmin, IsStaff)
3. **Password Hashing**: Django's built-in password hashing
4. **Unique Constraints**: Database-level unique constraint on ticket_id
5. **Transaction Safety**: Atomic operations with select_for_update to prevent race conditions
6. **Input Validation**: Comprehensive serializer validation

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Successful GET/PUT/PATCH
- `201 Created`: Successful POST
- `400 Bad Request`: Validation errors
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Error Response Format:**
```json
{
    "error": "Error message here"
}
```

or

```json
{
    "field_name": ["Error message for this field"]
}
```

---

## Testing

### Using cURL

```bash
# Login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "staff1", "password": "password123"}'

# Generate Ticket (with token)
curl -X POST http://localhost:8000/api/staff/generate-ticket/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"event_id": 1, "entry_type_id": 1}'
```

### Using Postman

1. Import the API endpoints
2. Set Authorization type to "Bearer Token"
3. Add the access token from login response

---

## Database Schema

### Models

1. **Event**: Festival events
2. **EntryType**: Ticket types for events (Adult, Kids, VIP, etc.)
3. **StaffProfile**: User profile with role and ticket range
4. **TicketCustomization**: Ticket appearance configuration per event
5. **Ticket**: Generated tickets with unique IDs

### Relationships

- Event → EntryType (One-to-Many)
- Event → TicketCustomization (One-to-One)
- Event → Ticket (One-to-Many)
- EntryType → Ticket (One-to-Many)
- User → StaffProfile (One-to-One)
- User → Ticket (One-to-Many)

---

## Production Deployment Checklist

1. Set `DEBUG = False` in settings.py
2. Configure proper `SECRET_KEY`
3. Set `ALLOWED_HOSTS`
4. Use environment variables for sensitive data
5. Configure PostgreSQL database
6. Set up static files serving
7. Enable HTTPS
8. Configure CORS if needed
9. Set up logging
10. Run `python manage.py collectstatic`
11. Use gunicorn or uwsgi for WSGI server
12. Set up Nginx as reverse proxy

---

## License

Proprietary - All rights reserved

---

## Support

For issues and questions, contact the development team.
