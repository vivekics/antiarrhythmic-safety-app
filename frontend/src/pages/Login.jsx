import { useState } from 'react'
import { login, getMe } from '../services/api'

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin123')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await login(username, password)
      const user = await getMe()
      // temporarily set token so getMe works
      localStorage.setItem('token', data.access_token)
      onLogin(data.access_token, user)
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>Safety Monitor</h1>
        <p>Antiarrhythmic Medication Safety System<br />(Synthetic Profiles Only)</p>

        {error && <div className="error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username</label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoFocus
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button className="btn btn-primary" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p className="text-muted mt-2" style={{ textAlign: 'center', fontSize: '0.8rem' }}>
          Default: admin / admin123
        </p>
      </div>
    </div>
  )
}
