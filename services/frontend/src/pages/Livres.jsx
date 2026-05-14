import { useEffect, useState } from 'react'
import axios from 'axios'

const card = { background: 'white', padding: '1rem', borderRadius: '8px', marginBottom: '0.8rem', boxShadow: '0 1px 4px rgba(0,0,0,0.1)' }
const input = { padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc', marginRight: '0.5rem', width: '200px' }
const btn = (color='#1a237e') => ({ padding: '0.5rem 1rem', background: color, color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginRight: '0.4rem' })

export default function Livres() {
  const [livres, setLivres] = useState([])
  const [form, setForm] = useState({ titre: '', auteur: '', isbn: '', genre: '' })
  const [recherche, setRecherche] = useState('')
  const [msg, setMsg] = useState('')

  const charger = () => axios.get('/api/livres').then(r => setLivres(r.data))

  useEffect(() => { charger() }, [])

  const ajouter = async () => {
    if (!form.titre || !form.auteur || !form.isbn) return setMsg('Titre, auteur et ISBN requis.')
    await axios.post('/api/livres', form)
    setForm({ titre: '', auteur: '', isbn: '', genre: '' })
    setMsg('Livre ajouté !')
    charger()
  }

  const supprimer = async (id) => {
    await axios.delete(`/api/livres/${id}`)
    charger()
  }

  const chercher = async () => {
    if (!recherche) return charger()
    const r = await axios.get(`/api/livres/recherche/${recherche}`)
    setLivres(r.data)
  }

  return (
    <div>
      <h2 style={{ marginBottom: '1rem' }}>Catalogue des Livres</h2>

      {/* Recherche */}
      <div style={{ marginBottom: '1.5rem' }}>
        <input style={input} placeholder="Rechercher titre/auteur/ISBN..." value={recherche}
          onChange={e => setRecherche(e.target.value)} />
        <button style={btn()} onClick={chercher}>Rechercher</button>
        <button style={btn('#666')} onClick={() => { setRecherche(''); charger() }}>Reset</button>
      </div>

      {/* Formulaire ajout */}
      <div style={{ ...card, background: '#e8eaf6' }}>
        <h3 style={{ marginBottom: '0.8rem' }}>Ajouter un livre</h3>
        {['titre','auteur','isbn','genre'].map(f => (
          <input key={f} style={input} placeholder={f.charAt(0).toUpperCase()+f.slice(1)}
            value={form[f]} onChange={e => setForm({...form, [f]: e.target.value})} />
        ))}
        <button style={btn('#2e7d32')} onClick={ajouter}>+ Ajouter</button>
        {msg && <span style={{ color: 'green', marginLeft: '1rem' }}>{msg}</span>}
      </div>

      {/* Liste */}
      {livres.length === 0 && <p style={{ color: '#999', marginTop: '1rem' }}>Aucun livre trouvé.</p>}
      {livres.map(l => (
        <div key={l.id} style={card}>
          <strong>{l.titre}</strong> — {l.auteur}
          <span style={{ marginLeft: '1rem', color: '#666', fontSize: '0.85rem' }}>ISBN: {l.isbn}</span>
          {l.genre && <span style={{ marginLeft: '0.5rem', color: '#1a237e', fontSize: '0.85rem' }}>[{l.genre}]</span>}
          <span style={{ marginLeft: '1rem', color: l.disponible ? 'green' : 'red', fontSize: '0.85rem' }}>
            {l.disponible ? 'Disponible :)' : 'Emprunté :('}
          </span>
          <button style={{...btn('#c62828'), float: 'right', fontSize: '0.8rem'}} onClick={() => supprimer(l.id)}>Supprimer</button>
        </div>
      ))}
    </div>
  )
}