import { useEffect, useState } from 'react'
import axios from 'axios'

const card = { background: 'white', padding: '1rem', borderRadius: '8px', marginBottom: '0.8rem', boxShadow: '0 1px 4px rgba(0,0,0,0.1)' }
const input = { padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc', marginRight: '0.5rem', width: '180px' }
const btn = (color='#1a237e') => ({ padding: '0.5rem 1rem', background: color, color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginRight: '0.4rem' })

export default function Utilisateurs() {
  const [users, setUsers] = useState([])
  const [form, setForm] = useState({ nom: '', prenom: '', email: '', type_utilisateur: 'Étudiant' })
  const [msg, setMsg] = useState('')

  const charger = () => axios.get('/api/utilisateurs').then(r => setUsers(r.data))
  useEffect(() => { charger() }, [])

  const creer = async () => {
    if (!form.nom || !form.email) return setMsg('Nom et email requis.')
    await axios.post('/api/utilisateurs', form)
    setForm({ nom: '', prenom: '', email: '', type_utilisateur: 'Étudiant' })
    setMsg('Utilisateur créé !')
    charger()
  }

  const supprimer = async (id) => {
    await axios.delete(`/api/utilisateurs/${id}`)
    charger()
  }

  return (
    <div>
      <h2 style={{ marginBottom: '1rem' }}>👥 Utilisateurs</h2>

      <div style={{ ...card, background: '#e8eaf6' }}>
        <h3 style={{ marginBottom: '0.8rem' }}>Ajouter un utilisateur</h3>
        {['nom','prenom','email'].map(f => (
          <input key={f} style={input} placeholder={f.charAt(0).toUpperCase()+f.slice(1)}
            value={form[f]} onChange={e => setForm({...form, [f]: e.target.value})} />
        ))}
        <select style={{...input, width: '140px'}} value={form.type_utilisateur}
          onChange={e => setForm({...form, type_utilisateur: e.target.value})}>
          <option>Étudiant</option>
          <option>Professeur</option>
          <option>Personnel</option>
        </select>
        <button style={btn('#2e7d32')} onClick={creer}>+ Créer</button>
        {msg && <span style={{ color: 'green', marginLeft: '1rem' }}>{msg}</span>}
      </div>

      {users.length === 0 && <p style={{ color: '#999', marginTop: '1rem' }}>Aucun utilisateur.</p>}
      {users.map(u => (
        <div key={u.id} style={card}>
          <strong>{u.prenom} {u.nom}</strong>
          <span style={{ marginLeft: '1rem', color: '#666' }}>{u.email}</span>
          <span style={{ marginLeft: '1rem', background: '#e8eaf6', padding: '0.2rem 0.5rem', borderRadius: '12px', fontSize: '0.8rem' }}>
            {u.type_utilisateur}
          </span>
          <button style={{...btn('#c62828'), float: 'right', fontSize: '0.8rem'}} onClick={() => supprimer(u.id)}>Supprimer</button>
        </div>
      ))}
    </div>
  )
}