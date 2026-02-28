import { useState, useEffect } from 'react'
import axios from 'axios'
import Layout from './Layout'

function AssignSubEvents() {
  const [staffList, setStaffList] = useState([])
  const [subEventsList, setSubEventsList] = useState([])
  const [selectedStaffId, setSelectedStaffId] = useState('')
  const [selectedSubEvents, setSelectedSubEvents] = useState(new Set())
  const [currentAssignments, setCurrentAssignments] = useState([])
  const [loading, setLoading] = useState(true)
  const [alert, setAlert] = useState({ show: false, message: '', type: '' })
  const [assignmentCount, setAssignmentCount] = useState(0)

  const API_BASE = 'http://localhost:8000/api'
  const token = localStorage.getItem('access_token')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      await Promise.all([loadStaff(), loadSubEvents()])
    } catch (error) {
      showAlert('Error loading data: ' + error.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  const loadStaff = async () => {
    try {
      const response = await axios.get(`${API_BASE}/admin/staff-list/`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setStaffList(response.data.filter(s => s.role === 'staff'))
    } catch (error) {
      showAlert('Error loading staff', 'error')
    }
  }

  const loadSubEvents = async () => {
    try {
      const response = await axios.get(`${API_BASE}/admin/sub-events/0/`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setSubEventsList(response.data)
    } catch (error) {
      showAlert('Error loading sub-events', 'error')
    }
  }

  const handleStaffChange = (e) => {
    const staffId = e.target.value
    setSelectedStaffId(staffId)

    if (!staffId) {
      setSelectedSubEvents(new Set())
      setCurrentAssignments([])
      return
    }

    const staff = staffList.find(s => s.id === parseInt(staffId))
    if (staff && staff.assigned_sub_events) {
      setSelectedSubEvents(new Set(staff.assigned_sub_events))
      const assignments = staff.assigned_sub_events.map(seId => {
        const se = subEventsList.find(s => s.id === seId)
        return se ? `${se.event_name} - ${se.name}` : ''
      }).filter(Boolean)
      setCurrentAssignments(assignments)
    } else {
      setSelectedSubEvents(new Set())
      setCurrentAssignments([])
    }
  }

  const toggleSubEvent = (subEventId) => {
    const newSelected = new Set(selectedSubEvents)
    if (newSelected.has(subEventId)) {
      newSelected.delete(subEventId)
    } else {
      newSelected.add(subEventId)
    }
    setSelectedSubEvents(newSelected)
  }

  const clearSelection = () => {
    setSelectedSubEvents(new Set())
  }

  const assignSubEvents = async () => {
    if (!selectedStaffId) {
      showAlert('Please select a staff member', 'error')
      return
    }

    try {
      await axios.post(
        `${API_BASE}/admin/assign-events/`,
        {
          staff_id: parseInt(selectedStaffId),
          sub_event_ids: Array.from(selectedSubEvents),
          replace: true
        },
        { headers: { Authorization: `Bearer ${token}` } }
      )

      showAlert(`✓ Successfully assigned ${selectedSubEvents.size} sub-events!`, 'success')
      setAssignmentCount(prev => prev + 1)
      await loadStaff()
      handleStaffChange({ target: { value: selectedStaffId } })
    } catch (error) {
      showAlert('Error: ' + (error.response?.data?.error || 'Assignment failed'), 'error')
    }
  }

  const showAlert = (message, type) => {
    setAlert({ show: true, message, type })
    setTimeout(() => setAlert({ show: false, message: '', type: '' }), 5000)
  }

  const selectedStaff = staffList.find(s => s.id === parseInt(selectedStaffId))

  return (
    <div className="page-container">
      <button className="back-btn" onClick={() => navigate('/')}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        Back
      </button>
      <div className="page-header">
        <h1>Assign Sub-Events to Staff</h1>
        <p>Manage staff access to festival sub-events</p>
      </div>

      {alert.show && (
        <div className={`alert alert-${alert.type}`}>
          {alert.message}
        </div>
      )}

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{staffList.length}</div>
          <div className="stat-label">Total Staff</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{subEventsList.length}</div>
          <div className="stat-label">Total Sub-Events</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{assignmentCount}</div>
          <div className="stat-label">Assignments Made</div>
        </div>
      </div>

      {/* Staff Selection */}
      <div className="form-group">
        <label>Select Staff Member</label>
        <select 
          value={selectedStaffId} 
          onChange={handleStaffChange}
          className="form-select"
        >
          <option value="">-- Select Staff --</option>
          {staffList.map(staff => (
            <option key={staff.id} value={staff.id}>
              {staff.user.username} ({staff.staff_code}) - Range: {staff.range_start}-{staff.range_end}
            </option>
          ))}
        </select>
      </div>

      {/* Staff Details & Assignment */}
      {selectedStaff && (
        <div className="staff-card">
          <div className="staff-info">
            <div className="staff-name">
              {selectedStaff.user.first_name} {selectedStaff.user.last_name} (@{selectedStaff.user.username})
            </div>
            <div className="staff-details">
              Staff Code: {selectedStaff.staff_code} | Range: {selectedStaff.range_start}-{selectedStaff.range_end} | Counter: {selectedStaff.current_counter}
            </div>
          </div>

          {/* Current Assignments */}
          {currentAssignments.length > 0 && (
            <div className="current-assignments">
              <h4>📌 Currently Assigned Sub-Events:</h4>
              <ul>
                {currentAssignments.map((assignment, idx) => (
                  <li key={idx}>✓ {assignment}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Sub-Events List */}
          <div className="form-group">
            <label>Available Sub-Events (Select multiple)</label>
            <div className="subevent-list">
              {loading ? (
                <div className="loading">Loading sub-events...</div>
              ) : subEventsList.length === 0 ? (
                <div className="loading">No sub-events available</div>
              ) : (
                subEventsList.map(se => (
                  <div
                    key={se.id}
                    className={`subevent-item ${selectedSubEvents.has(se.id) ? 'selected' : ''}`}
                    onClick={() => toggleSubEvent(se.id)}
                  >
                    <input
                      type="checkbox"
                      checked={selectedSubEvents.has(se.id)}
                      onChange={() => toggleSubEvent(se.id)}
                      onClick={(e) => e.stopPropagation()}
                    />
                    <div>
                      <div className="subevent-name">{se.event_name} - {se.name}</div>
                      <div className="subevent-details">
                        Code: {se.code} | {new Date(se.start_time).toLocaleDateString()} - {new Date(se.end_time).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="action-buttons">
            <button className="btn-primary" onClick={assignSubEvents}>
              💾 Save Assignments
            </button>
            <button className="btn-secondary" onClick={clearSelection}>
              🔄 Clear Selection
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default AssignSubEvents
