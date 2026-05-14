import { useEffect, useState } from 'react'
import axios from 'axios'

const card = { background: 'white', padding: '1rem', borderRadius: '8px', marginBottom: '0.8rem', boxShadow: '0 1px 4px rgba(0,0,0,0.1)' }
const input = { padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc', marginRight: '0.5rem', width: '120px' }
const btn = (color='#1a237e') => ({ padding: '0.5rem 1rem', background: color, color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginRight: '0.4rem' })

export default function Emprunts() {
  const [emprunts, setEmprunts] = useState([])
  const [form, setForm] = useState({ user_id: '', livre_id: '', duree_jours: 14 })
  const [msg, setMsg] = useState('')

  const charger = () => axios.get('/api/emprunts').then(r => setEmprunts(r.data))
  useEffect(() => { charger() }, [])

  const emprunter = async () => {
    if (!form.user_id || !form.livre_id) return setMsg('User ID et Livre ID requis.')
    await axios.post('/api/emprunts', { user_id: parseInt(form.user_id), livre_id: parseInt(form.livre_id), duree_jours: parseInt(form.duree_jours) })
    setForm({ user_id: '', livre_id: '', duree_jours: 14 })
    setMsg('Emprunt enregistré !')
    charger()
  }

  const retourner = async (id) => {
    await axios.put(`/api/emprunts/${id}/retour`)
    setMsg('Retour enregistré !')
    charger()
  }

  return (
    <div>
      <h2 style={{ marginBottom: '1rem' }}>📋 Emprunts</h2>

      <div style={{ ...card, background: '#e8eaf6' }}>
        <h3 style={{ marginBottom: '0.8rem' }}>Nouvel emprunt</h3>
        <input style={input} placeholder="User ID" type="number" value={form.user_id} onChange={e => setForm({...form, user_id: e.target.value})} />
        <input style={input} placeholder="Livre ID" type="number" value={form.livre_id} onChange={e => setForm({...form, livre_id: e.target.value})} />
        <input style={input} placeholder="Durée (jours)" type="number" value={form.duree_jours} onChange={e => setForm({...form, duree_jours: e.target.value})} />
        <button style={btn('#2e7d32')} onClick={emprunter}>Emprunter</button>
        {msg && <span style={{ color: 'green', marginLeft: '1rem' }}>{msg}</span>}
      </div>

      {emprunts.length === 0 && <p style={{ color: '#999', marginTop: '1rem' }}>Aucun emprunt.</p>}
      {emprunts.map(e => (
        <div key={e.id} style={card}>
          <strong>Emprunt #{e.id}</strong>
          <span style={{ margin: '0 1rem', color: '#555' }}>👤 User {e.user_id} — 📖 Livre {e.livre_id}</span>
          <span style={{ color: '#888', fontSize: '0.85rem' }}>
            Retour prévu : {new Date(e.date_retour_prevue).toLocaleDateString('fr-FR')}
          </span>
          <span style={{ marginLeft: '1rem', color: e.retourne ? 'green' : '#f57c00', fontWeight: 'bold' }}>
            {e.retourne ? 'Rendu :)' : 'En cours :|'}
          </span>
          {!e.retourne && (
            <button style={{...btn('#f57c00'), float: 'right', fontSize: '0.8rem'}} onClick={() => retourner(e.id)}>
              Marquer rendu
            </button>
          )}
        </div>
      ))}
    </div>
  )
}