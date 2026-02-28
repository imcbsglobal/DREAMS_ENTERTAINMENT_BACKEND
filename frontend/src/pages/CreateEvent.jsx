import { useState } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

function CreateEvent() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    name: '',
    place: '',
    address: '',
    start_date: '',
    end_date: ''
  })
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')

    try {
      const token = localStorage.getItem('access_token')
      await axios.post('http://localhost:8000/api/admin/create-event/', formData, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setMessage('Event created successfully!')
      setTimeout(() => navigate('/list-events'), 1500)
    } catch (err) {
      setMessage(err.response?.data?.error || 'Failed to create event')
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
        <h1>Create New Event</h1>
        <p>Set up a new festival or event for ticket management</p>
      </div>

      {message && (
        <div className={message.includes('success') ? 'alert alert-success' : 'alert alert-error'}>
          {message}
        </div>
      )}
      
      <div className="form-card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Event Name *</label>
            <input
              type="text"
              placeholder="e.g., Summer Music Festival 2024"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Venue/Place *</label>
              <input
                type="text"
                placeholder="e.g., Central Park"
                value={formData.place}
                onChange={(e) => setFormData({...formData, place: e.target.value})}
                required
              />
            </div>

            <div className="form-group">
              <label>Full Address *</label>
              <input
                type="text"
                placeholder="e.g., 123 Park Avenue, NY"
                value={formData.address}
                onChange={(e) => setFormData({...formData, address: e.target.value})}
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Start Date *</label>
              <input
                type="date"
                value={formData.start_date}
                onChange={(e) => setFormData({...formData, start_date: e.target.value})}
                required
              />
            </div>

            <div className="form-group">
              <label>End Date *</label>
              <input
                type="date"
                value={formData.end_date}
                onChange={(e) => setFormData({...formData, end_date: e.target.value})}
                required
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="button" className="btn-secondary" onClick={() => navigate('/')}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create Event'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default CreateEvent
