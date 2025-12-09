import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Chat from './pages/Chat'
import YogaSentinel from './pages/YogaSentinel'
import Dashboard from './pages/Dashboard'
import Culture from './pages/Culture'
import Emergency from './pages/Emergency'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/yoga-sentinel" element={<YogaSentinel />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/culture" element={<Culture />} />
          <Route path="/emergency" element={<Emergency />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
