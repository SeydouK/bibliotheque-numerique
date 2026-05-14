import { useState } from 'react'
import axios from 'axios'

const btn = (color='#1a237e') => ({ padding: '0.5rem 1rem', background: color, color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginRight: '0.4rem' })
const card = { background: 'white', padding: '1rem', borderRadius: '8px', marginBottom: '0.8rem', boxShadow: '0 1px 4px rgba(0,0,0,0.1)' }

export default function Recommandations() {
  const [userId, setUserId] = useState('')
  const [reco, setReco] = useState(null)
  const [trainMsg, setTrainMsg] = useState('')
  const [loading, setLoading] = useState(false)

  const chercher = async () => {
    if (!userId) return
    setLoading(true)
    try {
      const r = await axios.get(`/api/reco/recommendations/${userId}`)
      setReco(r.data)
    } catch (e) {
      setReco({ error: 'Erreur lors de la récupération' })
    }
    setLoading(false)
  }

  const reentrainer = async () => {
    setTrainMsg('Entraînement en cours...')
    await axios.post('/api/reco/train')
    setTrainMsg(' Entraînement lancé en arrière-plan !')
  }

  return (
    <div>
      <h2 style={{ marginBottom: '1rem' }}> Recommandations</h2>

      <div style={{ ...card, background: '#e8eaf6', marginBottom: '1.5rem' }}>
        <h3 style={{ marginBottom: '0.8rem' }}>Obtenir des recommandations</h3>
        <input
          style={{ padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc', marginRight: '0.5rem', width: '150px' }}
          type="number" placeholder="User ID" value={userId}
          onChange={e => setUserId(e.target.value)}
        />
        <button style={btn()} onClick={chercher} disabled={loading}>
          {loading ? 'Chargement...' : 'Voir recommandations'}
        </button>
      </div>

      {reco && !reco.error && (
        <div style={card}>
          <h3>Livres recommandés pour l'utilisateur #{reco.user_id}</h3>
          <p style={{ color: '#666', fontSize: '0.85rem', marginBottom: '0.5rem' }}>Méthode : {reco.methode}</p>
          {reco.recommandations.length === 0
            ? <p style={{ color: '#999' }}>Aucune recommandation disponible.</p>
            : reco.recommandations.map(id => (
              <span key={id} style={{ display: 'inline-block', margin: '0.3rem', padding: '0.4rem 0.8rem', background: '#1a237e', color: 'white', borderRadius: '16px' }}>
                 Livre #{id}
              </span>
            ))
          }
        </div>
      )}
      {reco?.error && <p style={{ color: 'red' }}>{reco.error}</p>}

      <div style={{ ...card, background: '#fff3e0', marginTop: '2rem' }}>
        <h3 style={{ marginBottom: '0.8rem' }}> Ré-entraîner le modèle</h3>
        <p style={{ color: '#666', marginBottom: '0.8rem', fontSize: '0.9rem' }}>
          Lance un nouvel entraînement à partir des emprunts réels.
        </p>
        <button style={btn('#e65100')} onClick={reentrainer}>Lancer l'entraînement</button>
        {trainMsg && <span style={{ marginLeft: '1rem', color: '#e65100' }}>{trainMsg}</span>}
      </div>
    </div>
  )
}