# Event Assignment Feature

## What Changed:
✅ Staff can now only see and generate tickets for **assigned events**
✅ Admin can assign specific events to specific staff members
✅ New endpoint: `POST /api/admin/assign-events/`

## How It Works:

### Admin Workflow:
1. Create Event (e.g., Event ID: 1)
2. Create Staff (e.g., Staff ID: 2)
3. **Assign Event to Staff**:
   - Staff ID: 2
   - Event IDs: 1 (or multiple: 1,2,3)
4. Staff can now only access assigned events

### Staff Workflow:
1. Login as staff
2. View Events → Only shows assigned events
3. Generate tickets → Only for assigned events

## API Usage:

### Assign Events to Staff
```http
POST /api/admin/assign-events/
Authorization: Bearer <admin_token>

{
  "staff_id": 2,
  "event_ids": [1, 2, 3]
}
```

**Response:**
```json
{
  "message": "Events assigned successfully",
  "staff_id": 2,
  "assigned_events": [1, 2, 3]
}
```

## Testing in HTML:

1. **Admin Tab** → Section 6.5 "Assign Events to Staff"
2. Enter Staff ID (e.g., 2)
3. Enter Event IDs (e.g., 1 or 1,2,3)
4. Click "Assign Events"

## Important:
- Staff without assigned events will see **empty event list**
- Staff can only generate tickets for **assigned events**
- Admin can reassign events anytime (replaces previous assignments)

## Database Changes:
- Added `assigned_events` ManyToMany field to StaffProfile
- Migration applied: `0002_staffprofile_assigned_events.py`

**Ready to use!** 🚀
