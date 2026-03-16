import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { Sessions } from './pages/Sessions'
import { Plugins } from './pages/Plugins'
import { Knowledge } from './pages/Knowledge'
import { Settings } from './pages/Settings'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="sessions" element={<Sessions />} />
        <Route path="plugins" element={<Plugins />} />
        <Route path="knowledge" element={<Knowledge />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  )
}

export default App
