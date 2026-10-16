import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
})

// Attach token automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const login = async (username, password) => {
  const form = new URLSearchParams()
  form.append('username', username)
  form.append('password', password)
  const { data } = await api.post('/api/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
  return data
}

export const getMe = () => api.get('/api/auth/me').then(r => r.data)

export const getPatients = () => api.get('/api/patients/').then(r => r.data)
export const getPatient = (id) => api.get(`/api/patients/${id}`).then(r => r.data)
export const createPatient = (payload) => api.post('/api/patients/', payload).then(r => r.data)
export const updatePatient = (id, payload) => api.put(`/api/patients/${id}`, payload).then(r => r.data)
export const deletePatient = (id) => api.delete(`/api/patients/${id}`).then(r => r.data)
export const assessPatient = (id) => api.post(`/api/patients/${id}/assess`).then(r => r.data)
export const getAssessments = (id) => api.get(`/api/patients/${id}/assessments`).then(r => r.data)

export default api
