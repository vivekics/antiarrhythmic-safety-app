import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { getPatient, assessPatient, deletePatient } from '../services/api'

export default function PatientDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [patient, setPatient] = useState(null)
  const [assessment, setAssessment] = useState(null)
  const [loading, setLoading] = useState(true)
  const [assessing, setAssessing] = useState(false)

  useEffect(() => {
    getPatient(id)
      .then(setPatient)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [id])

  const runAssessment = async () => {
    setAssessing(true)
    try {
      const result = await assessPatient(id)
      setAssessment(result)
    } catch (err) {
      alert(err.response?.data?.detail || 'Assessment failed')
    } finally {
      setAssessing(false)
    }
  }

  const handleDelete = async () => {
    if (!window.confirm('Delete this synthetic profile?')) return
    await deletePatient(id)
    navigate('/')
  }

  if (loading) return <p>Loading...</p>
  if (!patient) return <p>Profile not found</p>

  return (
    <div>
      <div className="flex" style={{ justifyContent: 'space-between', marginBottom: '1.5rem' }}>
        <div>
          <h2>{patient.profile_code}</h2>
          <p className="text-muted">
            {patient.age}y {patient.sex} · {patient.cardiac_diagnosis || 'No diagnosis'} · {patient.antiarrhythmic_drug || 'No antiarrhythmic'}
          </p>
        </div>
        <div className="flex">
          <Link to={`/patients/${id}/edit`} className="btn btn-outline">Edit</Link>
          <button className="btn btn-danger" onClick={handleDelete}>Delete</button>
          <button className="btn btn-primary" onClick={runAssessment} disabled={assessing}>
            {assessing ? 'Assessing...' : 'Run Safety Assessment'}
          </button>
        </div>
      </div>

      {/* Assessment Result */}
      {assessment && (
        <div className="card">
          <div className="flex" style={{ justifyContent: 'space-between', marginBottom: '1rem' }}>
            <h2>Safety Assessment Result</h2>
            <span className={`badge badge-${assessment.overall_risk}`}>
              {assessment.overall_risk} risk
            </span>
          </div>

          {assessment.alerts.length === 0 ? (
            <p className="text-muted">No safety concerns detected with the current data.</p>
          ) : (
            assessment.alerts.map((a, i) => (
              <div key={i} className={`alert-item alert-${a.severity}`}>
                <strong>[{a.severity.toUpperCase()}] {a.message}</strong>
                <div>{a.recommendation}</div>
              </div>
            ))
          )}

          {assessment.recommendations.length > 0 && (
            <div className="mt-2">
              <h3 style={{ fontSize: '0.95rem', marginBottom: '0.5rem' }}>Key Recommendations</h3>
              <ul style={{ paddingLeft: '1.25rem' }}>
                {assessment.recommendations.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Profile Details */}
      <div className="card">
        <h2>Profile Details</h2>
        <div className="form-grid" style={{ marginTop: '1rem' }}>
          <div><strong>LVEF</strong><br />{patient.lvef != null ? `${patient.lvef}%` : '—'}</div>
          <div><strong>Heart Rate</strong><br />{patient.heart_rate != null ? `${patient.heart_rate} bpm` : '—'}</div>
          <div><strong>QTc</strong><br />{patient.qtc != null ? `${patient.qtc} ms` : '—'}</div>
          <div><strong>QRS</strong><br />{patient.qrs_duration != null ? `${patient.qrs_duration} ms` : '—'}</div>
          <div><strong>Potassium</strong><br />{patient.potassium != null ? `${patient.potassium} mmol/L` : '—'}</div>
          <div><strong>Magnesium</strong><br />{patient.magnesium != null ? `${patient.magnesium} mmol/L` : '—'}</div>
          <div><strong>eGFR</strong><br />{patient.egfr != null ? `${patient.egfr}` : '—'}</div>
          <div><strong>TSH</strong><br />{patient.tsh != null ? patient.tsh : '—'}</div>
          <div><strong>ALT</strong><br />{patient.alt != null ? patient.alt : '—'}</div>
          <div><strong>Drug + Dose</strong><br />{patient.antiarrhythmic_drug} {patient.antiarrhythmic_dose}</div>
          <div style={{ gridColumn: '1 / -1' }}>
            <strong>Other Medications</strong><br />
            {patient.other_medications || '—'}
          </div>
        </div>

        <h3 style={{ marginTop: '1.5rem', marginBottom: '0.75rem' }}>Last Monitoring</h3>
        <div className="form-grid">
          <div><strong>ECG</strong><br />{patient.last_ecg_date || '—'}</div>
          <div><strong>Thyroid</strong><br />{patient.last_thyroid_date || '—'}</div>
          <div><strong>LFTs</strong><br />{patient.last_lft_date || '—'}</div>
          <div><strong>Electrolytes</strong><br />{patient.last_electrolytes_date || '—'}</div>
          <div><strong>Renal</strong><br />{patient.last_renal_date || '—'}</div>
        </div>

        {patient.notes && (
          <>
            <h3 style={{ marginTop: '1.5rem', marginBottom: '0.5rem' }}>Notes</h3>
            <p>{patient.notes}</p>
          </>
        )}
      </div>
    </div>
  )
}
