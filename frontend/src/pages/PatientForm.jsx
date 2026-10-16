import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { createPatient, getPatient, updatePatient } from '../services/api'

const emptyForm = {
  profile_code: '',
  age: 65,
  sex: 'M',
  cardiac_diagnosis: '',
  lvef: '',
  heart_rate: '',
  qt_interval: '',
  qtc: '',
  qrs_duration: '',
  potassium: '',
  magnesium: '',
  creatinine: '',
  egfr: '',
  alt: '',
  ast: '',
  tsh: '',
  free_t4: '',
  antiarrhythmic_drug: '',
  antiarrhythmic_dose: '',
  other_medications: '',
  last_ecg_date: '',
  last_thyroid_date: '',
  last_lft_date: '',
  last_electrolytes_date: '',
  last_renal_date: '',
  notes: ''
}

export default function PatientForm() {
  const { id } = useParams()
  const isEdit = Boolean(id)
  const navigate = useNavigate()
  const [form, setForm] = useState(emptyForm)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isEdit) {
      getPatient(id).then((p) => {
        const cleaned = {}
        Object.keys(emptyForm).forEach((k) => {
          cleaned[k] = p[k] != null ? p[k] : ''
        })
        setForm(cleaned)
      })
    }
  }, [id, isEdit])

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    // Convert empty strings to null and numbers
    const payload = {}
    Object.entries(form).forEach(([k, v]) => {
      if (v === '') {
        payload[k] = null
      } else if (['age', 'heart_rate', 'qt_interval', 'qtc', 'qrs_duration'].includes(k)) {
        payload[k] = parseInt(v, 10)
      } else if (['lvef', 'potassium', 'magnesium', 'creatinine', 'egfr', 'alt', 'ast', 'tsh', 'free_t4'].includes(k)) {
        payload[k] = parseFloat(v)
      } else {
        payload[k] = v
      }
    })

    try {
      if (isEdit) {
        await updatePatient(id, payload)
        navigate(`/patients/${id}`)
      } else {
        const created = await createPatient(payload)
        navigate(`/patients/${created.id}`)
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Save failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2 className="mb-2">{isEdit ? 'Edit Synthetic Profile' : 'New Synthetic Profile'}</h2>

      {error && <div className="error">{error}</div>}

      <form onSubmit={handleSubmit} className="card">
        <h3 style={{ marginBottom: '1rem' }}>Demographics & Diagnosis</h3>
        <div className="form-grid">
          <div className="form-group">
            <label>Profile Code (optional)</label>
            <input name="profile_code" value={form.profile_code} onChange={handleChange} placeholder="Auto-generated if empty" />
          </div>
          <div className="form-group">
            <label>Age *</label>
            <input type="number" name="age" value={form.age} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Sex</label>
            <select name="sex" value={form.sex} onChange={handleChange}>
              <option value="M">Male</option>
              <option value="F">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div className="form-group">
            <label>Cardiac Diagnosis</label>
            <input name="cardiac_diagnosis" value={form.cardiac_diagnosis} onChange={handleChange} placeholder="e.g. AF, VT, SVT" />
          </div>
        </div>

        <h3 style={{ margin: '1.5rem 0 1rem' }}>Cardiac Parameters</h3>
        <div className="form-grid">
          <div className="form-group">
            <label>LVEF (%)</label>
            <input type="number" step="0.1" name="lvef" value={form.lvef} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Heart Rate (bpm)</label>
            <input type="number" name="heart_rate" value={form.heart_rate} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>QT Interval (ms)</label>
            <input type="number" name="qt_interval" value={form.qt_interval} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>QTc (ms)</label>
            <input type="number" name="qtc" value={form.qtc} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>QRS Duration (ms)</label>
            <input type="number" name="qrs_duration" value={form.qrs_duration} onChange={handleChange} />
          </div>
        </div>

        <h3 style={{ margin: '1.5rem 0 1rem' }}>Laboratory Values</h3>
        <div className="form-grid">
          <div className="form-group">
            <label>Potassium (mmol/L)</label>
            <input type="number" step="0.1" name="potassium" value={form.potassium} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Magnesium (mmol/L)</label>
            <input type="number" step="0.01" name="magnesium" value={form.magnesium} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Creatinine (µmol/L)</label>
            <input type="number" step="0.1" name="creatinine" value={form.creatinine} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>eGFR (mL/min/1.73m²)</label>
            <input type="number" step="0.1" name="egfr" value={form.egfr} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>ALT (U/L)</label>
            <input type="number" step="0.1" name="alt" value={form.alt} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>AST (U/L)</label>
            <input type="number" step="0.1" name="ast" value={form.ast} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>TSH (mIU/L)</label>
            <input type="number" step="0.01" name="tsh" value={form.tsh} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Free T4</label>
            <input type="number" step="0.1" name="free_t4" value={form.free_t4} onChange={handleChange} />
          </div>
        </div>

        <h3 style={{ margin: '1.5rem 0 1rem' }}>Medications</h3>
        <div className="form-grid">
          <div className="form-group">
            <label>Antiarrhythmic Drug</label>
            <select name="antiarrhythmic_drug" value={form.antiarrhythmic_drug} onChange={handleChange}>
              <option value="">— Select —</option>
              <option value="Sotalol">Sotalol</option>
              <option value="Flecainide">Flecainide</option>
              <option value="Amiodarone">Amiodarone</option>
              <option value="Dronedarone">Dronedarone</option>
              <option value="Propafenone">Propafenone</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div className="form-group">
            <label>Dose</label>
            <input name="antiarrhythmic_dose" value={form.antiarrhythmic_dose} onChange={handleChange} placeholder="e.g. 80 mg BD" />
          </div>
          <div className="form-group" style={{ gridColumn: '1 / -1' }}>
            <label>Other Medications</label>
            <textarea name="other_medications" value={form.other_medications} onChange={handleChange} rows={2}
              placeholder="e.g. Bisoprolol 5mg, Digoxin 62.5mcg, Ramipril..." />
          </div>
        </div>

        <h3 style={{ margin: '1.5rem 0 1rem' }}>Last Monitoring Dates</h3>
        <div className="form-grid">
          <div className="form-group">
            <label>Last ECG</label>
            <input type="date" name="last_ecg_date" value={form.last_ecg_date || ''} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Last Thyroid Function</label>
            <input type="date" name="last_thyroid_date" value={form.last_thyroid_date || ''} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Last LFTs</label>
            <input type="date" name="last_lft_date" value={form.last_lft_date || ''} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Last Electrolytes</label>
            <input type="date" name="last_electrolytes_date" value={form.last_electrolytes_date || ''} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Last Renal Function</label>
            <input type="date" name="last_renal_date" value={form.last_renal_date || ''} onChange={handleChange} />
          </div>
        </div>

        <div className="form-group mt-2">
          <label>Notes</label>
          <textarea name="notes" value={form.notes} onChange={handleChange} rows={3} />
        </div>

        <div className="flex mt-2">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Saving...' : (isEdit ? 'Update Profile' : 'Create Profile')}
          </button>
          <button type="button" className="btn btn-outline" onClick={() => navigate(-1)}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}
