import { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate, useLocation } from 'react-router-dom'

function CreateSubEvent() {
  const navigate = useNavigate()
  const location = useLocation()
  const [events, setEvents] = useState([])
  const [formData, setFormData] = useState({
    event: location.state?.eventId || '',
    name: '',
    description: '',
    start_time: '',
    end_time: ''
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

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')

    try {
      const token = localStorage.getItem('access_token')
      await axios.post('http://localhost:8000/api/admin/create-sub-event/', formData, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setMessage('Sub event created successfully!')
      setFormData({ event: '', name: '', description: '', start_time: '', end_time: '' })
    } catch (err) {
      const errorMsg = err.response?.data?.error || err.response?.data?.detail || JSON.stringify(err.response?.data) || 'Failed to create sub event'
      setMessage(errorMsg)
      console.error('Error details:', err.response?.data)
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
        <h1>Create Sub Event</h1>
        <p>Add a sub-event or session to your main event</p>
      </div>

      {message && (
        <div className={message.includes('success') ? 'alert alert-success' : 'alert alert-error'}>
          {message}
        </div>
      )}
      
      <div className="form-card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Parent Event *</label>
            <select
              value={formData.event}
              onChange={(e) => setFormData({...formData, event: e.target.value})}
              required
            >
              <option value="">Select parent event</option>
              {events.map(event => (
                <option key={event.id} value={event.id}>{event.name}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Sub Event Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              placeholder="e.g., DJ Night, Rock Concert"
              required
            />
          </div>

          <div className="form-group">
            <label>Description *</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              placeholder="Enter description"
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Start Time *</label>
              <input
                type="datetime-local"
                value={formData.start_time}
                onChange={(e) => setFormData({...formData, start_time: e.target.value})}
                required
              />
            </div>

            <div className="form-group">
              <label>End Time *</label>
              <input
                type="datetime-local"
                value={formData.end_time}
                onChange={(e) => setFormData({...formData, end_time: e.target.value})}
                required
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="button" className="btn-secondary" onClick={() => navigate('/list-events')}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create Sub Event'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default CreateSubEvent
