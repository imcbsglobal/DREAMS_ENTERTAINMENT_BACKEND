import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

function Layout({ userData, onLogout, children }) {
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="dashboard">
      <div className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h2>Festival Ticket</h2>
          <p>Admin Dashboard</p>
        </div>
        
        <div className="user-profile">
          <div className="avatar">{userData?.username?.charAt(0).toUpperCase()}</div>
          <div className="user-details">
            <p className="username">{userData?.username}</p>
            <span className="role">{userData?.role}</span>
          </div>
        </div>

        <nav className="nav-menu">
          <div className="nav-section">
            <h3>Event Management</h3>
            <button className="nav-item" onClick={() => navigate('/create-event')}>Create Event</button>
            <button className="nav-item" onClick={() => navigate('/list-events')}>List Ongoing Events</button>
            <button className="nav-item" onClick={() => navigate('/create-entry-type')}>Create Entry Type</button>
            <button className="nav-item" onClick={() => navigate('/ticket-customization')}>Customize Ticket</button>
          </div>

          <div className="nav-section">
            <h3>Staff Management</h3>
            <button className="nav-item" onClick={() => navigate('/create-staff')}>Create Staff</button>
            <button className="nav-item" onClick={() => navigate('/list-staff')}>List Staff</button>
            <button className="nav-item" onClick={() => navigate('/assign-subevents')}>Assign Sub-Events to Staff</button>
          </div>

          <div className="nav-section">
            <h3>Reports</h3>
            <button className="nav-item" onClick={() => navigate('/tickets-report')}>Tickets Report</button>
            <button className="nav-item" onClick={() => navigate('/revenue-report')}>Revenue Report</button>
            <button className="nav-item" onClick={() => navigate('/staff-summary')}>Staff Summary Report</button>
          </div>
        </nav>

        <button className="logout-btn" onClick={onLogout}>Logout</button>
      </div>

      <div className="main-content">
        <button 
          className="mobile-menu-btn" 
          onClick={() => setSidebarOpen(!sidebarOpen)}
          style={{
            display: 'none',
            position: 'fixed',
            top: '20px',
            left: '20px',
            zIndex: '200',
            background: 'white',
            border: '1px solid #e2e8f0',
            borderRadius: '12px',
            padding: '12px',
            cursor: 'pointer'
          }}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          </svg>
        </button>
        {children}
      </div>
    </div>
  )
}

export default Layout
