import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import Livres from './pages/Livres.jsx'
import Utilisateurs from './pages/Utilisateurs.jsx'
import Emprunts from './pages/Emprunts.jsx'
import Recommandations from './pages/Recommandations.jsx'

const navStyle = {
  display: 'flex', gap: '1rem', padding: '1rem 2rem',
  background: '#1a237e', alignItems: 'center'
}
const linkStyle = ({ isActive }) => ({
  color: isActive ? '#ffeb3b' : 'white',
  textDecoration: 'none', fontWeight: isActive ? 'bold' : 'normal',
  padding: '0.4rem 0.8rem', borderRadius: '4px',
  background: isActive ? 'rgba(255,255,255,0.1)' : 'transparent'
})

export default function App() {
  return (
    <BrowserRouter>
      <nav style={navStyle}>
        <span style={{ color: 'white', fontWeight: 'bold', fontSize: '1.2rem', marginRight: '2rem' }}>
          📚 Bibliothèque DIT
        </span>
        <NavLink to="/"            style={linkStyle}>Livres</NavLink>
        <NavLink to="/utilisateurs" style={linkStyle}>Utilisateurs</NavLink>
        <NavLink to="/emprunts"     style={linkStyle}>Emprunts</NavLink>
        <NavLink to="/reco"         style={linkStyle}>Recommandations</NavLink>
      </nav>
      <main style={{ padding: '2rem' }}>
        <Routes>
          <Route path="/"             element={<Livres />} />
          <Route path="/utilisateurs" element={<Utilisateurs />} />
          <Route path="/emprunts"     element={<Emprunts />} />
          <Route path="/reco"         element={<Recommandations />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}