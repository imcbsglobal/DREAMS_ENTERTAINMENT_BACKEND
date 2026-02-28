import { useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import './App.css'
import Login from './pages/Login'
import Layout from './pages/Layout'
import Dashboard from './pages/Dashboard'
import CreateEvent from './pages/CreateEvent'
import ListEvents from './pages/ListEvents'
import CreateEntryType from './pages/CreateEntryType'
import CreateSubEvent from './pages/CreateSubEvent'
import AssignSubEvents from './pages/AssignSubEvents'
import CreateStaff from './pages/CreateStaff'
import ListStaff from './pages/ListStaff'
import TicketsReport from './pages/TicketsReport'
import TicketCustomization from './pages/TicketCustomization'
import RevenueReport from './pages/RevenueReport'
import StaffSummaryReport from './pages/StaffSummaryReport'

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [userData, setUserData] = useState(null)

  const handleLoginSuccess = (user) => {
    setUserData(user)
    setIsLoggedIn(true)
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setIsLoggedIn(false)
    setUserData(null)
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route 
          path="/login" 
          element={isLoggedIn ? <Navigate to="/" /> : <Login onLoginSuccess={handleLoginSuccess} />} 
        />
        <Route 
          path="/" 
          element={isLoggedIn ? <Layout userData={userData} onLogout={handleLogout}><Dashboard userData={userData} /></Layout> : <Navigate to="/login" />} 
        />
        <Route 
          path="/create-event" 
          element={isLoggedIn ? <CreateEvent /> : <Navigate to="/login" />} 
        />
        <Route 
          path="/list-events" 
          element={isLoggedIn ? <ListEvents /> : <Navigate to="/login" />} 
        />
        <Route 
          path="/create-entry-type" 
          element={isLoggedIn ? <CreateEntryType /> : <Navigate to="/login" />} 
        />
        <Route 
          path="/create-sub-event" 
          element={isLoggedIn ? <CreateSubEvent /> : <Navigate to="/login" />} 
        />
        <Route 
          path="/assign-subevents" 
          element={isLoggedIn ? <AssignSubEvents /> : <Navigate to="/login" />} 
        />
        <Route 
          path="/create-staff" 
          element={isLoggedIn ? <CreateStaff /> : <Navigate to="/login" />} 
        />
        <Route 
          path="/list-staff" 
          element={isLoggedIn ? <ListStaff /> : <Navigate to="/login" />} 
        />
        <Route 
          path="/tickets-report" 
          element={isLoggedIn ? <TicketsReport /> : <Navigate to="/login" />} 
        />
        <Route 
          path="/ticket-customization" 
          element={isLoggedIn ? <Layout userData={userData} onLogout={handleLogout}><TicketCustomization /></Layout> : <Navigate to="/login" />} 
        />
        <Route 
          path="/revenue-report" 
          element={isLoggedIn ? <Layout userData={userData} onLogout={handleLogout}><RevenueReport /></Layout> : <Navigate to="/login" />} 
        />
        <Route 
          path="/staff-summary" 
          element={isLoggedIn ? <Layout userData={userData} onLogout={handleLogout}><StaffSummaryReport /></Layout> : <Navigate to="/login" />} 
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App
