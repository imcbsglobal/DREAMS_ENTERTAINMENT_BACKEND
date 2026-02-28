import { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate, useLocation } from 'react-router-dom'

function CreateEntryType() {
  const navigate = useNavigate()
  const location = useLocation()
  const [events, setEvents] = useState([])
  const [subEvents, setSubEvents] = useState([])
  const [formData, setFormData] = useState({
    event: location.state?.eventId || '',
    sub_event: '',
    name: '',
    price: '',
    description: '',
    is_active: true
  })
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

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
      }
    }

    fetchEvents()
  }, [])

  useEffect(() => {
    const fetchSubEvents = async () => {
      if (formData.event) {
        try {
          const token = localStorage.getItem('access_token')
          const response = await axios.get(`http://localhost:8000/api/admin/sub-events/${formData.event}/`, {
            headers: { Authorization: `Bearer ${token}` }
          })
          setSubEvents(response.data)
        } catch (err) {
          console.error('Failed to fetch sub-events:', err)
          setSubEvents([])
        }
      } else {
        setSubEvents([])
      }
    }

    fetchSubEvents()
  }, [formData.event])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')

    try {
      const token = localStorage.getItem('access_token')
      await axios.post('http://localhost:8000/api/admin/create-entry-type/', formData, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setMessage('Entry type created successfully!')
      setFormData({ event: '', sub_event: '', name: '', price: '', description: '', is_active: true })
    } catch (err) {
      setMessage(err.response?.data?.error || 'Failed to create entry type')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-container">
      <button className="back-btn" onClick={() => navigate('/list-events')}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        Back
      </button>
      <div className="page-header">
        <h1>Create Entry Type</h1>
        <p>Add ticket categories for your event</p>
      </div>

      {message && (
        <div className={message.includes('success') ? 'alert alert-success' : 'alert alert-error'}>
          {message}
        </div>
      )}
      
      <div className="form-card">
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label>Event *</label>
              <select
                value={formData.event}
                onChange={(e) => setFormData({...formData, event: e.target.value, sub_event: ''})}
                required
              >
                <option value="">Select an event</option>
                {events.map(event => (
                  <option key={event.id} value={event.id}>{event.name}</option>
                ))}
              </select>
            </div>

            {subEvents.length > 0 && (
              <div className="form-group">
                <label>Sub Event</label>
                <select
                  value={formData.sub_event}
                  onChange={(e) => setFormData({...formData, sub_event: e.target.value})}
                >
                  <option value="">Select a sub event</option>
                  {subEvents.map(subEvent => (
                    <option key={subEvent.id} value={subEvent.id}>{subEvent.name}</option>
                  ))}
                </select>
              </div>
            )}
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Entry Type Name *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                placeholder="e.g., Adult, Kids, VIP"
                required
              />
            </div>

            <div className="form-group">
              <label>Price *</label>
              <input
                type="number"
                step="0.01"
                value={formData.price}
                onChange={(e) => setFormData({...formData, price: e.target.value})}
                placeholder="0.00"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              placeholder="Enter description (optional)"
            />
          </div>

          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
              />
              <span>Active</span>
            </label>
          </div>

          <div className="form-actions">
            <button type="button" className="btn-secondary" onClick={() => navigate('/list-events')}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create Entry Type'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default CreateEntryType
