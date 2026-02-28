import { useState } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

function CreateStaff() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    email: '',
    first_name: '',
    last_name: '',
    role: 'staff',
    range_start: '',
    range_end: ''
  })
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')

    try {
      const token = localStorage.getItem('access_token')
      await axios.post('http://localhost:8000/api/admin/create-staff/', formData, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setMessage('Staff created successfully!')
      setTimeout(() => navigate('/'), 1500)
    } catch (err) {
      setMessage(err.response?.data?.error || JSON.stringify(err.response?.data) || 'Failed to create staff')
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
        <h1>Create Staff Member</h1>
        <p>Add a new staff member to the system</p>
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
              <label>Username *</label>
              <input
                type="text"
                placeholder="e.g., john_doe"
                value={formData.username}
                onChange={(e) => setFormData({...formData, username: e.target.value})}
                required
              />
            </div>

            <div className="form-group">
              <label>Password *</label>
              <input
                type="password"
                placeholder="Enter password"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
                required
                minLength="6"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Email *</label>
            <input
              type="email"
              placeholder="e.g., john@example.com"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>First Name *</label>
              <input
                type="text"
                placeholder="e.g., John"
                value={formData.first_name}
                onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                required
              />
            </div>

            <div className="form-group">
              <label>Last Name *</label>
              <input
                type="text"
                placeholder="e.g., Doe"
                value={formData.last_name}
                onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label>Role *</label>
            <select
              value={formData.role}
              onChange={(e) => setFormData({...formData, role: e.target.value})}
              required
            >
              <option value="staff">Staff</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Ticket Range Start *</label>
              <input
                type="number"
                placeholder="e.g., 5001"
                value={formData.range_start}
                onChange={(e) => setFormData({...formData, range_start: e.target.value})}
                required
                min="1"
              />
            </div>

            <div className="form-group">
              <label>Ticket Range End *</label>
              <input
                type="number"
                placeholder="e.g., 6000"
                value={formData.range_end}
                onChange={(e) => setFormData({...formData, range_end: e.target.value})}
                required
                min="1"
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="button" className="btn-secondary" onClick={() => navigate('/')}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create Staff'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default CreateStaff
