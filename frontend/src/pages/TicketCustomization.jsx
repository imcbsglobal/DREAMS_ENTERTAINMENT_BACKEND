import { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

function TicketCustomization() {
  const navigate = useNavigate()
  const [events, setEvents] = useState([])
  const [selectedEvent, setSelectedEvent] = useState('')
  const [formData, setFormData] = useState({
    event: '',
    header_text: '',
    footer_text: '',
    show_event_name: true,
    show_place: true,
    show_entry_type: true,
    show_price: true,
    printer_format: ''
  })
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [preview, setPreview] = useState(null)

  useEffect(() => {
    fetchEvents()
  }, [])

  const fetchEvents = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const res = await axios.get('http://localhost:8000/api/admin/event-list/', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setEvents(res.data)
    } catch (err) {
      setMessage('Failed to load events')
    }
  }

  const handleEventChange = (eventId) => {
    setSelectedEvent(eventId)
    setFormData({...formData, event: eventId})
    const event = events.find(e => e.id === parseInt(eventId))
    if (event) {
      generatePreview(event)
    }
  }

  const generatePreview = (event) => {
    setPreview({
      event_name: event?.name || 'Event Name',
      place: event?.place || 'Venue',
      entry_type: 'Adult',
      price: '50.00'
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')

    try {
      const token = localStorage.getItem('access_token')
      await axios.post('http://localhost:8000/api/admin/configure-ticket/', formData, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setMessage('Ticket customization saved successfully!')
      setTimeout(() => navigate('/'), 2000)
    } catch (err) {
      setMessage(err.response?.data?.error || 'Failed to save customization')
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
        <h1>Ticket Customization</h1>
        <p>Configure how tickets will appear when printed</p>
      </div>

      {message && (
        <div className={message.includes('success') ? 'alert alert-success' : 'alert alert-error'}>
          {message}
        </div>
      )}

      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px'}}>
        <div className="form-card">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Select Event *</label>
              <select
                value={selectedEvent}
                onChange={(e) => handleEventChange(e.target.value)}
                required
              >
                <option value="">Choose an event...</option>
                {events.map(event => (
                  <option key={event.id} value={event.id}>
                    {event.name} ({event.code})
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Header Text</label>
              <input
                type="text"
                placeholder="e.g., Welcome to Summer Festival 2024"
                value={formData.header_text}
                onChange={(e) => setFormData({...formData, header_text: e.target.value})}
              />
            </div>

            <div className="form-group">
              <label>Footer Text</label>
              <input
                type="text"
                placeholder="e.g., Thank you for your visit!"
                value={formData.footer_text}
                onChange={(e) => setFormData({...formData, footer_text: e.target.value})}
              />
            </div>

            <div className="form-group">
              <label style={{fontWeight: 'bold', marginBottom: '10px'}}>Display Options</label>
              <div style={{display: 'flex', flexDirection: 'column', gap: '8px'}}>
                <label style={{display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer'}}>
                  <input
                    type="checkbox"
                    checked={formData.show_event_name}
                    onChange={(e) => setFormData({...formData, show_event_name: e.target.checked})}
                  />
                  Show Event Name
                </label>
                <label style={{display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer'}}>
                  <input
                    type="checkbox"
                    checked={formData.show_place}
                    onChange={(e) => setFormData({...formData, show_place: e.target.checked})}
                  />
                  Show Venue/Place
                </label>
                <label style={{display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer'}}>
                  <input
                    type="checkbox"
                    checked={formData.show_entry_type}
                    onChange={(e) => setFormData({...formData, show_entry_type: e.target.checked})}
                  />
                  Show Entry Type
                </label>
                <label style={{display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer'}}>
                  <input
                    type="checkbox"
                    checked={formData.show_price}
                    onChange={(e) => setFormData({...formData, show_price: e.target.checked})}
                  />
                  Show Price
                </label>
              </div>
            </div>

            <div className="form-actions">
              <button type="button" className="btn-secondary" onClick={() => navigate('/')}>
                Cancel
              </button>
              <button type="submit" className="btn-primary" disabled={loading || !selectedEvent}>
                {loading ? 'Saving...' : 'Save Customization'}
              </button>
            </div>
          </form>
        </div>

        {/* Preview Panel */}
        <div className="form-card" style={{backgroundColor: '#f8f9fa'}}>
          <h3 style={{marginBottom: '20px', fontSize: '18px'}}>Ticket Preview</h3>
          {preview ? (
            <div style={{
              border: '2px dashed #ddd',
              padding: '30px',
              backgroundColor: 'white',
              borderRadius: '8px',
              fontFamily: 'monospace',
              fontSize: '14px',
              lineHeight: '1.8'
            }}>
              {formData.header_text && (
                <div style={{textAlign: 'center', fontWeight: 'bold', marginBottom: '15px', borderBottom: '1px solid #eee', paddingBottom: '10px'}}>
                  {formData.header_text}
                </div>
              )}
              
              <div style={{marginBottom: '10px'}}>
                <strong>Ticket ID:</strong> U2-SF-SUM-5001
              </div>
              
              {formData.show_event_name && (
                <div style={{marginBottom: '10px'}}>
                  <strong>Event:</strong> {preview.event_name}
                </div>
              )}
              
              {formData.show_place && (
                <div style={{marginBottom: '10px'}}>
                  <strong>Venue:</strong> {preview.place}
                </div>
              )}
              
              {formData.show_entry_type && (
                <div style={{marginBottom: '10px'}}>
                  <strong>Type:</strong> {preview.entry_type}
                </div>
              )}
              
              {formData.show_price && (
                <div style={{marginBottom: '10px'}}>
                  <strong>Price:</strong> ${preview.price}
                </div>
              )}
              
              <div style={{marginBottom: '10px'}}>
                <strong>Date:</strong> {new Date().toLocaleString()}
              </div>
              
              {formData.footer_text && (
                <div style={{textAlign: 'center', fontStyle: 'italic', marginTop: '15px', borderTop: '1px solid #eee', paddingTop: '10px', fontSize: '12px'}}>
                  {formData.footer_text}
                </div>
              )}
            </div>
          ) : (
            <div style={{textAlign: 'center', color: '#999', padding: '40px'}}>
              Select an event to see preview
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default TicketCustomization
