import { useState, useEffect } from 'react'
import { Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import PatientForm from './pages/PatientForm'
import PatientDetail from './pages/PatientDetail'
import { getMe } from './services/api'

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      getMe()
        .then(setUser)
        .catch(() => localStorage.removeItem('token'))
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const handleLogin = (token, userData) => {
    localStorage.setItem('token', token)
    setUser(userData)
    navigate('/')
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    setUser(null)
    navigate('/login')
  }

  if (loading) {
    return <div className="container" style={{ paddingTop: '3rem' }}>Loading...</div>
  }

  if (!user) {
    return (
      <Routes>
        <Route path="/login" element={<Login onLogin={handleLogin} />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    )
  }

  return (
    <>
      <header className="header">
        <h1>Antiarrhythmic Safety Monitor</h1>
        <nav>
          <Link to="/">Dashboard</Link>
          <Link to="/patients/new">New Profile</Link>
          <span style={{ marginLeft: '1.5rem', opacity: 0.9 }}>
            {user.full_name || user.username}
          </span>
          <button
            onClick={handleLogout}
            className="btn btn-sm"
            style={{ marginLeft: '1rem', background: 'rgba(255,255,255,0.2)', color: 'white' }}
          >
            Logout
          </button>
        </nav>
      </header>

      <main className="container">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/patients/new" element={<PatientForm />} />
          <Route path="/patients/:id" element={<PatientDetail />} />
          <Route path="/patients/:id/edit" element={<PatientForm />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </>
  )
}

export default App
