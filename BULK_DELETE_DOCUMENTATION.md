# Bulk Delete Tickets Feature Documentation

## Overview

The Bulk Delete Tickets feature allows administrators to safely delete historical ticket data by date range and event, without affecting current functionality or data integrity.

## Endpoint

```
POST/DELETE /api/admin/tickets/bulk-delete/
```

## Safety Features

### 🛡️ Built-in Safety Mechanisms

1. **Date Restrictions**:
   - Cannot delete today's tickets
   - Cannot delete future tickets
   - Cannot delete yesterday's tickets (safety buffer)

2. **Confirmation Required**:
   - Requires explicit confirmation token: `DELETE_TICKETS_CONFIRMED`
   - Two-step process: Preview → Confirm

3. **Data Integrity**:
   - Staff counters preserved for sequence integrity
   - Reports automatically update
   - Atomic transactions prevent partial deletions

4. **Admin-Only Access**:
   - Requires `IsAdmin` permission
   - JWT authentication required

## Usage Flow

### Step 1: Preview Deletion (POST)

**Request:**
```json
{
    "event_id": 1,
    "start_date": "2024-01-10",
    "end_date": "2024-01-12"
}
```

**Response:**
```json
{
    "message": "Preview of tickets to be deleted",
    "preview": {
        "event_name": "Summer Festival",
        "event_code": "SF",
        "date_range": "2024-01-10 to 2024-01-12",
        "total_tickets": 150,
        "total_revenue": "7500.00",
        "affected_staff": ["staff1", "staff2"],
        "sub_event_breakdown": [
            {
                "sub_event__name": "ENTRY TICKET",
                "ticket_count": 100,
                "revenue": "5000.00"
            }
        ],
        "entry_type_breakdown": [
            {
                "entry_type__name": "Adult",
                "ticket_count": 100,
                "revenue": "5000.00"
            }
        ],
        "safety_notes": [
            "Today's tickets are excluded for safety",
            "Future tickets are excluded for safety",
            "Staff counters will be preserved",
            "Reports will automatically update"
        ]
    },
    "note": "Use DELETE method with confirmation_token to proceed with deletion"
}
```

### Step 2: Confirm Deletion (DELETE)

**Request:**
```json
{
    "event_id": 1,
    "start_date": "2024-01-10",
    "end_date": "2024-01-12",
    "confirmation_token": "DELETE_TICKETS_CONFIRMED"
}
```

**Response:**
```json
{
    "message": "150 tickets deleted successfully",
    "summary": {
        "event_name": "Summer Festival",
        "event_code": "SF",
        "date_range": "2024-01-10 to 2024-01-12",
        "total_revenue_impact": "7500.00",
        "affected_staff": [
            {
                "username": "staff1",
                "staff_code": "U2",
                "tickets_deleted": 100,
                "revenue_impact": "5000.00"
            }
        ],
        "counter_policy": "Staff counters preserved for sequence integrity",
        "deletion_timestamp": "2024-01-16T10:30:00Z",
        "tickets_deleted": 150
    },
    "note": "Reports will automatically reflect the changes. Staff counters preserved for sequence integrity."
}
```

## Error Handling

### Validation Errors

```json
{
    "error": "Cannot delete today's tickets for safety reasons"
}
```

```json
{
    "error": "Cannot delete future tickets"
}
```

```json
{
    "error": "Cannot delete tickets from yesterday or today for safety"
}
```

### Confirmation Errors

```json
{
    "error": "Invalid confirmation token",
    "required_token": "DELETE_TICKETS_CONFIRMED",
    "note": "This is a safety measure to prevent accidental deletions"
}
```

## Impact on Reports

### ✅ Automatic Updates

All existing reports automatically reflect deleted data:

1. **Tickets Report** (`/api/admin/reports/tickets/`):
   - Deleted tickets won't appear
   - Total counts automatically reduce
   - Pagination works correctly

2. **Revenue Report** (`/api/admin/reports/revenue/`):
   - Revenue automatically recalculates
   - Event-wise revenue updates

3. **Staff Summary Report** (`/api/admin/reports/staff-summary/`):
   - Ticket counts automatically reduce
   - Staff revenue automatically recalculates
   - `remaining_tickets` calculation preserved

### 📊 Staff Counter Policy

**Current Counter Preserved**: Staff `current_counter` values are NOT modified to maintain sequence integrity.

**Example**:
- Staff range: 5001-6000
- Generated 100 tickets (current_counter = 100)
- Delete 50 tickets
- **Result**: 
  - Reports show 50 tickets generated ✅
  - current_counter remains 100 ✅
  - Next ticket will still be 5101 ✅

## Testing with cURL

### Preview Deletion
```bash
curl -X POST http://localhost:8000/api/admin/tickets/bulk-delete/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "event_id": 1,
    "start_date": "2024-01-10",
    "end_date": "2024-01-12"
  }'
```

### Confirm Deletion
```bash
curl -X DELETE http://localhost:8000/api/admin/tickets/bulk-delete/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "event_id": 1,
    "start_date": "2024-01-10",
    "end_date": "2024-01-12",
    "confirmation_token": "DELETE_TICKETS_CONFIRMED"
  }'
```

## Use Cases

### 1. Daily Cleanup
Delete yesterday's test tickets during event setup:
```json
{
    "event_id": 1,
    "start_date": "2024-01-14",
    "end_date": "2024-01-14"
}
```

### 2. Historical Data Cleanup
Remove old event data after event completion:
```json
{
    "event_id": 1,
    "start_date": "2024-01-01",
    "end_date": "2024-01-10"
}
```

### 3. Mistake Correction
Remove tickets generated by mistake (older than yesterday):
```json
{
    "event_id": 1,
    "start_date": "2024-01-12",
    "end_date": "2024-01-12"
}
```

## Best Practices

### 🔒 Security
- Always preview before deletion
- Use in off-peak hours for large deletions
- Backup database before bulk operations
- Monitor affected staff and revenue impact

### 📅 Timing
- Only delete data older than yesterday
- Consider event lifecycle before deletion
- Coordinate with staff during active events

### 📊 Monitoring
- Check reports after deletion
- Verify staff counter integrity
- Monitor system performance during large deletions

## Database Impact

### Performance
- Uses indexed fields (`created_at__date`, `event_id`)
- Atomic transactions prevent corruption
- Batch deletion for efficiency

### Storage
- Immediate space reclamation
- No soft-delete overhead
- Clean removal from all related queries

## Frontend Integration

Use the provided `bulk_delete_test.html` for testing, or integrate into your admin dashboard:

```javascript
// Preview deletion
const previewResponse = await fetch('/api/admin/tickets/bulk-delete/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
        event_id: eventId,
        start_date: startDate,
        end_date: endDate
    })
});

// Confirm deletion
const deleteResponse = await fetch('/api/admin/tickets/bulk-delete/', {
    method: 'DELETE',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
        event_id: eventId,
        start_date: startDate,
        end_date: endDate,
        confirmation_token: 'DELETE_TICKETS_CONFIRMED'
    })
});
```

## Troubleshooting

### Common Issues

1. **"Cannot delete today's tickets"**
   - Solution: Use dates older than yesterday

2. **"Invalid confirmation token"**
   - Solution: Use exact token `DELETE_TICKETS_CONFIRMED`

3. **"Event not found"**
   - Solution: Verify event_id exists

4. **"No tickets found"**
   - Solution: Check date range and event has tickets in that period

### Support

For issues or questions:
1. Check API response for detailed error messages
2. Verify date ranges and safety restrictions
3. Ensure proper admin authentication
4. Review the preview data before deletion

---

**⚠️ Important**: This feature permanently deletes data. Always preview first and ensure you have proper backups before bulk operations.