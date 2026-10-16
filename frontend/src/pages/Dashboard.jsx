import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getPatients } from '../services/api'

export default function Dashboard() {
  const [patients, setPatients] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getPatients()
      .then(setPatients)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p>Loading profiles...</p>

  return (
    <div>
      <div className="flex" style={{ justifyContent: 'space-between', marginBottom: '1.5rem' }}>
        <h2>Synthetic Patient Profiles</h2>
        <Link to="/patients/new" className="btn btn-primary">+ New Profile</Link>
      </div>

      <div className="card">
        {patients.length === 0 ? (
          <p className="text-muted">No profiles yet. Create your first synthetic patient.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Code</th>
                <th>Age</th>
                <th>Diagnosis</th>
                <th>Drug</th>
                <th>LVEF</th>
                <th>QTc</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {patients.map((p) => (
                <tr key={p.id}>
                  <td><strong>{p.profile_code}</strong></td>
                  <td>{p.age}</td>
                  <td>{p.cardiac_diagnosis || '—'}</td>
                  <td>{p.antiarrhythmic_drug || '—'}</td>
                  <td>{p.lvef != null ? `${p.lvef}%` : '—'}</td>
                  <td>{p.qtc != null ? `${p.qtc} ms` : '—'}</td>
                  <td>
                    <Link to={`/patients/${p.id}`} className="btn btn-sm btn-outline">
                      View / Assess
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
