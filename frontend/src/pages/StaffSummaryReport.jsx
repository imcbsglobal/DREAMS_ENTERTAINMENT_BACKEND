import { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

function StaffSummaryReport() {
  const navigate = useNavigate()
  const [staffList, setStaffList] = useState([])
  const [selectedStaff, setSelectedStaff] = useState('')
  const [summaryData, setSummaryData] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchStaffList()
    fetchSummary()
  }, [])

  const fetchStaffList = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const res = await axios.get('http://localhost:8000/api/admin/staff-list/', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setStaffList(res.data)
    } catch (err) {
      console.error('Failed to fetch staff:', err)
    }
  }

  const fetchSummary = async (staffId = '') => {
    setLoading(true)
    try {
      const token = localStorage.getItem('access_token')
      const url = staffId 
        ? `http://localhost:8000/api/admin/reports/staff-summary/?staff_id=${staffId}`
        : 'http://localhost:8000/api/admin/reports/staff-summary/'
      
      const res = await axios.get(url, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setSummaryData(res.data)
    } catch (err) {
      console.error('Failed to fetch summary:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleStaffChange = (staffId) => {
    setSelectedStaff(staffId)
    fetchSummary(staffId)
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
        <h1>Staff Summary Report</h1>
        <p>View staff performance and ticket statistics</p>
      </div>

      <div className="form-card" style={{marginBottom: '20px'}}>
        <div className="form-group">
          <label>Filter by Staff</label>
          <select value={selectedStaff} onChange={(e) => handleStaffChange(e.target.value)}>
            <option value="">All Staff</option>
            {staffList.map(staff => (
              <option key={staff.id} value={staff.id}>
                {staff.user.username} ({staff.staff_code})
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div style={{textAlign: 'center', padding: '40px'}}>Loading...</div>
      ) : summaryData?.staff_summary?.length > 0 ? (
        <div className="form-card">
          <h2 style={{marginBottom: '20px', fontSize: '20px'}}>Staff Performance</h2>
          <div style={{overflowX: 'auto'}}>
            <table style={{width: '100%', borderCollapse: 'collapse', fontSize: '14px'}}>
              <thead>
                <tr style={{backgroundColor: '#f8f9fa', borderBottom: '2px solid #dee2e6'}}>
                  <th style={{padding: '12px', textAlign: 'left'}}>Staff Name</th>
                  <th style={{padding: '12px', textAlign: 'center'}}>Staff Code</th>
                  <th style={{padding: '12px', textAlign: 'center'}}>Role</th>
                  <th style={{padding: '12px', textAlign: 'center'}}>Range</th>
                  <th style={{padding: '12px', textAlign: 'center'}}>Current Counter</th>
                  <th style={{padding: '12px', textAlign: 'center'}}>Tickets Generated</th>
                  <th style={{padding: '12px', textAlign: 'center'}}>Remaining</th>
                  <th style={{padding: '12px', textAlign: 'right'}}>Total Revenue</th>
                </tr>
              </thead>
              <tbody>
                {summaryData.staff_summary.map((staff, index) => (
                  <tr key={index} style={{borderBottom: '1px solid #dee2e6'}}>
                    <td style={{padding: '12px'}}>{staff.username}</td>
                    <td style={{padding: '12px', textAlign: 'center'}}>
                      <span style={{
                        backgroundColor: '#e0e7ff',
                        color: '#4338ca',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: 'bold'
                      }}>
                        {staff.staff_code}
                      </span>
                    </td>
                    <td style={{padding: '12px', textAlign: 'center', textTransform: 'capitalize'}}>
                      {staff.role}
                    </td>
                    <td style={{padding: '12px', textAlign: 'center'}}>
                      {staff.range_start} - {staff.range_end}
                    </td>
                    <td style={{padding: '12px', textAlign: 'center'}}>{staff.current_counter}</td>
                    <td style={{padding: '12px', textAlign: 'center', fontWeight: 'bold', color: '#3b82f6'}}>
                      {staff.tickets_generated}
                    </td>
                    <td style={{padding: '12px', textAlign: 'center'}}>
                      <span style={{
                        backgroundColor: staff.remaining_tickets < 10 ? '#fee2e2' : '#dcfce7',
                        color: staff.remaining_tickets < 10 ? '#dc2626' : '#16a34a',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: 'bold'
                      }}>
                        {staff.remaining_tickets}
                      </span>
                    </td>
                    <td style={{padding: '12px', textAlign: 'right', fontWeight: 'bold', color: '#10b981'}}>
                      ₹{staff.total_revenue}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div style={{marginTop: '30px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px'}}>
            <div style={{padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px', textAlign: 'center'}}>
              <div style={{fontSize: '14px', color: '#64748b', marginBottom: '8px'}}>Total Staff</div>
              <div style={{fontSize: '28px', fontWeight: 'bold', color: '#1e293b'}}>
                {summaryData.staff_summary.length}
              </div>
            </div>
            <div style={{padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px', textAlign: 'center'}}>
              <div style={{fontSize: '14px', color: '#64748b', marginBottom: '8px'}}>Total Tickets</div>
              <div style={{fontSize: '28px', fontWeight: 'bold', color: '#3b82f6'}}>
                {summaryData.staff_summary.reduce((sum, s) => sum + s.tickets_generated, 0)}
              </div>
            </div>
            <div style={{padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px', textAlign: 'center'}}>
              <div style={{fontSize: '14px', color: '#64748b', marginBottom: '8px'}}>Total Revenue</div>
              <div style={{fontSize: '28px', fontWeight: 'bold', color: '#10b981'}}>
                ₹{summaryData.staff_summary.reduce((sum, s) => sum + parseFloat(s.total_revenue), 0).toFixed(2)}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="form-card" style={{textAlign: 'center', padding: '40px', color: '#999'}}>
          No staff data available
        </div>
      )}
    </div>
  )
}

export default StaffSummaryReport
