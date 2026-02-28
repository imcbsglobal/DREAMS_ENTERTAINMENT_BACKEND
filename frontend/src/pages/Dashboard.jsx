import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import axios from 'axios'

function Dashboard({ userData }) {
  const navigate = useNavigate()
  const [stats, setStats] = useState({
    totalEvents: 0,
    totalStaff: 0,
    ticketsSold: 0,
    totalRevenue: 0
  })

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const token = localStorage.getItem('access_token')
        const headers = { Authorization: `Bearer ${token}` }

        const [eventsRes, staffRes, revenueRes] = await Promise.all([
          axios.get('http://localhost:8000/api/admin/event-list/', { headers }),
          axios.get('http://localhost:8000/api/admin/staff-list/', { headers }),
          axios.get('http://localhost:8000/api/admin/reports/revenue/', { headers })
        ])

        setStats({
          totalEvents: eventsRes.data.length || 0,
          totalStaff: staffRes.data.length || 0,
          ticketsSold: revenueRes.data.revenue_by_event?.reduce((sum, e) => sum + (e.ticket_count || 0), 0) || 0,
          totalRevenue: revenueRes.data.total_revenue || 0
        })
      } catch (err) {
        console.error('Failed to fetch stats:', err)
      }
    }

    fetchStats()
  }, [])

  return (
    <>
      <div className="content-header">
        <h1>Welcome Back, {userData?.username}!</h1>
        <p>Manage your festival ticket system from here</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon blue">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
              <line x1="16" y1="2" x2="16" y2="6" />
              <line x1="8" y1="2" x2="8" y2="6" />
              <line x1="3" y1="10" x2="21" y2="10" />
            </svg>
          </div>
          <div className="stat-info">
            <h3>Total Events</h3>
            <p className="stat-number">{stats.totalEvents}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon green">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
          </div>
          <div className="stat-info">
            <h3>Total Staff</h3>
            <p className="stat-number">{stats.totalStaff}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon purple">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
              <polyline points="13 2 13 9 20 9" />
            </svg>
          </div>
          <div className="stat-info">
            <h3>Tickets Sold</h3>
            <p className="stat-number">{stats.ticketsSold}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon orange">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="12" y1="1" x2="12" y2="23" />
              <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
            </svg>
          </div>
          <div className="stat-info">
            <h3>Total Revenue</h3>
            <p className="stat-number">₹{stats.totalRevenue}</p>
          </div>
        </div>
      </div>

      <div className="quick-actions">
        <h2>Quick Actions</h2>
        <div className="action-grid">
          <button className="action-card" onClick={() => navigate('/create-event')}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="16" />
              <line x1="8" y1="12" x2="16" y2="12" />
            </svg>
            <span>Create New Event</span>
          </button>
          <button className="action-card" onClick={() => navigate('/create-staff')}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="8.5" cy="7" r="4" />
              <line x1="20" y1="8" x2="20" y2="14" />
              <line x1="23" y1="11" x2="17" y2="11" />
            </svg>
            <span>Add Staff Member</span>
          </button>
          <button className="action-card" onClick={() => navigate('/tickets-report')}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
              <polyline points="10 9 9 9 8 9" />
            </svg>
            <span>View Reports</span>
          </button>
          <button className="action-card" onClick={() => navigate('/ticket-customization')}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
            </svg>
            <span>Customize Tickets</span>
          </button>
        </div>
      </div>
    </>
  )
}

export default Dashboard
