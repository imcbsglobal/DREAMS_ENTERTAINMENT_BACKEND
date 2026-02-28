import { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

function ListStaff() {
  const navigate = useNavigate()
  const [staff, setStaff] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStaff = async () => {
      try {
        const token = localStorage.getItem('access_token')
        const response = await axios.get('http://localhost:8000/api/admin/staff-list/', {
          headers: { Authorization: `Bearer ${token}` }
        })
        setStaff(response.data)
      } catch (err) {
        console.error('Failed to fetch staff:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchStaff()
  }, [])

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading">Loading staff...</div>
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
        <h1>Staff Members</h1>
        <p>Manage your team members and their ticket ranges</p>
      </div>
      
      {staff.length === 0 ? (
        <div className="empty-state">
          <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" strokeWidth="1.5">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
          <h3>No Staff Members Yet</h3>
          <p>Add your first staff member to get started!</p>
          <button className="btn-primary" onClick={() => navigate('/create-staff')}>
            Create Staff
          </button>
        </div>
      ) : (
        <div className="staff-grid">
          {staff.map(member => (
            <div key={member.id} className="staff-member-card">
              <div className="staff-member-header">
                <div className="staff-avatar">
                  {member.user.first_name?.charAt(0) || member.user.username?.charAt(0).toUpperCase()}
                </div>
                <div className="staff-member-info">
                  <h3>{member.user.first_name} {member.user.last_name}</h3>
                  <p className="staff-username">@{member.user.username}</p>
                </div>
                <span className={`role-badge ${member.role}`}>{member.role}</span>
              </div>
              
              <div className="staff-member-details">
                <div className="detail-row">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                    <polyline points="22,6 12,13 2,6"/>
                  </svg>
                  <span>{member.user.email}</span>
                </div>
                
                <div className="detail-row">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
                    <polyline points="13 2 13 9 20 9"/>
                  </svg>
                  <span>Staff Code: {member.staff_code}</span>
                </div>
                
                <div className="detail-row">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="12" y1="1" x2="12" y2="23"/>
                    <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                  </svg>
                  <span>Range: {member.range_start} - {member.range_end}</span>
                </div>
                
                <div className="detail-row">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                  </svg>
                  <span>Counter: {member.current_counter}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ListStaff
