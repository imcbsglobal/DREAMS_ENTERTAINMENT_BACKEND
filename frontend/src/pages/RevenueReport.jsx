import { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

function RevenueReport() {
  const navigate = useNavigate()
  const [events, setEvents] = useState([])
  const [selectedEvent, setSelectedEvent] = useState('')
  const [revenueData, setRevenueData] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchEvents()
    fetchRevenue()
  }, [])

  const fetchEvents = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const res = await axios.get('http://localhost:8000/api/admin/event-list/', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setEvents(res.data)
    } catch (err) {
      console.error('Failed to fetch events:', err)
    }
  }

  const fetchRevenue = async (eventId = '') => {
    setLoading(true)
    try {
      const token = localStorage.getItem('access_token')
      const url = eventId 
        ? `http://localhost:8000/api/admin/reports/revenue/?event_id=${eventId}`
        : 'http://localhost:8000/api/admin/reports/revenue/'
      
      const res = await axios.get(url, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setRevenueData(res.data)
    } catch (err) {
      console.error('Failed to fetch revenue:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleEventChange = (eventId) => {
    setSelectedEvent(eventId)
    fetchRevenue(eventId)
  }

  return (
    <div className="page-container">
      <button className="back-btn" onClick={() => navigate('/')}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        Back
      </button>

      <div className="page-header">
        <h1>Revenue Report</h1>
        <p>View revenue statistics by event</p>
      </div>

      <div className="form-card" style={{marginBottom: '20px'}}>
        <div className="form-group">
          <label>Filter by Event</label>
          <select value={selectedEvent} onChange={(e) => handleEventChange(e.target.value)}>
            <option value="">All Events</option>
            {events.map(event => (
              <option key={event.id} value={event.id}>
                {event.name} ({event.code})
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div style={{textAlign: 'center', padding: '40px'}}>Loading...</div>
      ) : revenueData ? (
        <>
          <div className="stats-grid" style={{marginBottom: '30px'}}>
            <div className="stat-card">
              <div className="stat-icon orange">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="12" y1="1" x2="12" y2="23" />
                  <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
                </svg>
              </div>
              <div className="stat-info">
                <h3>Total Revenue</h3>
                <p className="stat-number">₹{revenueData.total_revenue}</p>
              </div>
            </div>

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
                <p className="stat-number">{revenueData.revenue_by_event?.length || 0}</p>
              </div>
            </div>
          </div>

          <div className="form-card">
            <h2 style={{marginBottom: '20px', fontSize: '20px'}}>Revenue by Event</h2>
            {revenueData.revenue_by_event?.length > 0 ? (
              <div style={{overflowX: 'auto'}}>
                <table style={{width: '100%', borderCollapse: 'collapse'}}>
                  <thead>
                    <tr style={{backgroundColor: '#f8f9fa', borderBottom: '2px solid #dee2e6'}}>
                      <th style={{padding: '12px', textAlign: 'left'}}>Event Name</th>
                      <th style={{padding: '12px', textAlign: 'left'}}>Event Code</th>
                      <th style={{padding: '12px', textAlign: 'right'}}>Tickets Sold</th>
                      <th style={{padding: '12px', textAlign: 'right'}}>Total Revenue</th>
                    </tr>
                  </thead>
                  <tbody>
                    {revenueData.revenue_by_event.map((event, index) => (
                      <tr key={index} style={{borderBottom: '1px solid #dee2e6'}}>
                        <td style={{padding: '12px'}}>{event.event__name}</td>
                        <td style={{padding: '12px'}}>{event.event__code}</td>
                        <td style={{padding: '12px', textAlign: 'right'}}>{event.ticket_count}</td>
                        <td style={{padding: '12px', textAlign: 'right', fontWeight: 'bold', color: '#10b981'}}>
                          ₹{event.total_revenue}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div style={{textAlign: 'center', padding: '40px', color: '#999'}}>
                No revenue data available
              </div>
            )}
          </div>
        </>
      ) : null}
    </div>
  )
}

export default RevenueReport
