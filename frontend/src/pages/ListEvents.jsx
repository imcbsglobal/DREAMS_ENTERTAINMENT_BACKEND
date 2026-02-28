import { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

function ListEvents() {
  const navigate = useNavigate()
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const token = localStorage.getItem('access_token')
        const response = await axios.get('http://localhost:8000/api/admin/event-list/', {
          headers: { Authorization: `Bearer ${token}` }
        })
        setEvents(response.data)
      } catch (err) {
        console.error('Failed to fetch events:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchEvents()
  }, [])

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading">Loading events...</div>
      </div>
    )
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
        <h1>Ongoing Events</h1>
        <p>Manage your active festival events</p>
      </div>
      
      {events.length === 0 ? (
        <div className="empty-state">
          <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" strokeWidth="1.5">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
            <line x1="16" y1="2" x2="16" y2="6" />
            <line x1="8" y1="2" x2="8" y2="6" />
            <line x1="3" y1="10" x2="21" y2="10" />
          </svg>
          <h3>No Events Yet</h3>
          <p>Create your first event to get started!</p>
          <button className="btn-primary" onClick={() => navigate('/create-event')}>
            Create Event
          </button>
        </div>
      ) : (
        <div className="events-grid">
          {events.map(event => (
            <div key={event.id} className="event-card">
              <div className="event-header">
                <h2>{event.name}</h2>
                <span className="event-code">{event.code}</span>
              </div>
              <div className="event-details">
                <div className="detail-item">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                    <circle cx="12" cy="10" r="3" />
                  </svg>
                  <span>{event.place}</span>
                </div>
                <div className="detail-item">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                    <line x1="16" y1="2" x2="16" y2="6" />
                    <line x1="8" y1="2" x2="8" y2="6" />
                    <line x1="3" y1="10" x2="21" y2="10" />
                  </svg>
                  <span>{event.start_date} to {event.end_date}</span>
                </div>
                <div className="detail-item">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                    <polyline points="9 22 9 12 15 12 15 22" />
                  </svg>
                  <span>{event.address}</span>
                </div>
              </div>
              <div className="event-actions">
                <button className="action-btn primary" onClick={() => navigate('/create-entry-type', { state: { eventId: event.id } })}>
                  Add Entry Type
                </button>
                <button className="action-btn secondary" onClick={() => navigate('/create-sub-event', { state: { eventId: event.id } })}>
                  Add Sub Event
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ListEvents
