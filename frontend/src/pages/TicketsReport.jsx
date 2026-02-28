import { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

function TicketsReport() {
  const navigate = useNavigate()
  const [tickets, setTickets] = useState([])
  const [events, setEvents] = useState([])
  const [selectedEvent, setSelectedEvent] = useState('')
  const [loading, setLoading] = useState(true)
  const [totalTickets, setTotalTickets] = useState(0)

  useEffect(() => {
    loadEvents()
  }, [])

  useEffect(() => {
    loadTickets()
  }, [selectedEvent])

  const loadEvents = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await axios.get('http://localhost:8000/api/admin/event-list/', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setEvents(response.data)
    } catch (err) {
      console.error('Failed to fetch events:', err)
    }
  }

  const loadTickets = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('access_token')
      const url = selectedEvent 
        ? `http://localhost:8000/api/admin/reports/tickets/?event_id=${selectedEvent}`
        : 'http://localhost:8000/api/admin/reports/tickets/'
      
      const response = await axios.get(url, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setTickets(response.data.tickets || [])
      setTotalTickets(response.data.total_tickets || 0)
    } catch (err) {
      console.error('Failed to fetch tickets:', err)
    } finally {
      setLoading(false)
    }
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
        <h1>Tickets Report</h1>
        <p>View all generated tickets and filter by event</p>
      </div>

      <div className="report-filters">
        <div className="form-group">
          <label>Filter by Event</label>
          <select 
            value={selectedEvent} 
            onChange={(e) => setSelectedEvent(e.target.value)}
            className="form-select"
          >
            <option value="">All Events</option>
            {events.map(event => (
              <option key={event.id} value={event.id}>{event.name}</option>
            ))}
          </select>
        </div>
        <div className="report-summary">
          <div className="summary-card">
            <div className="summary-value">{totalTickets}</div>
            <div className="summary-label">Total Tickets</div>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="loading">Loading tickets...</div>
      ) : tickets.length === 0 ? (
        <div className="empty-state">
          <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" strokeWidth="1.5">
            <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
            <polyline points="13 2 13 9 20 9"/>
          </svg>
          <h3>No Tickets Found</h3>
          <p>No tickets have been generated yet</p>
        </div>
      ) : (
        <div className="table-container">
          <table className="report-table">
            <thead>
              <tr>
                <th>Ticket ID</th>
                <th>Event</th>
                <th>Sub Event</th>
                <th>Entry Type</th>
                <th>Staff</th>
                <th>Price</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {tickets.map(ticket => (
                <tr key={ticket.id}>
                  <td className="ticket-id-cell">{ticket.ticket_id}</td>
                  <td>{ticket.event_name}</td>
                  <td>{ticket.sub_event_name}</td>
                  <td>{ticket.entry_type_name}</td>
                  <td>{ticket.staff_username}</td>
                  <td className="price-cell">₹{ticket.price}</td>
                  <td>{new Date(ticket.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default TicketsReport
