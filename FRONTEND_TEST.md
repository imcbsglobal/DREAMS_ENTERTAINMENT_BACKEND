# 🎯 Simple Frontend Tester - Quick Start

## Step 1: Install CORS Package
```bash
cd "c:\Users\Muhammed Anazil T A\Desktop\Ticket-POS"
pip install django-cors-headers
```

## Step 2: Start Django Server
```bash
python manage.py runserver
```

## Step 3: Open HTML Tester
Open this file in your browser:
```
c:\Users\Muhammed Anazil T A\Desktop\Ticket-POS\admin_tester.html
```

Or just double-click: `admin_tester.html`

## Step 4: Test All Admin APIs

### 1. Login First
- Username: `admin` (pre-filled)
- Password: `admin123` (pre-filled)
- Click "Login" button
- You'll see the access token displayed

### 2. Test Each Endpoint
Click buttons in order:
1. ✅ Login (done)
2. ✅ Create Event
3. ✅ List Events
4. ✅ Create Entry Type (use Event ID from step 2)
5. ✅ Create Staff
6. ✅ List Staff
7. ✅ Configure Ticket
8. ✅ Tickets Report
9. ✅ Revenue Report
10. ✅ Staff Summary

### Results
- ✅ Green background = Success
- ❌ Red background = Error
- All responses shown in JSON format

## That's It! 🚀

All 10 admin endpoints can be tested with simple button clicks!
