import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import MarketDetail from './pages/MarketDetail'
import ExtractMarket from './pages/ExtractMarket'
import Rankings from './pages/Rankings'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/rankings" element={<Rankings />} />
          <Route path="/market/:marketId" element={<MarketDetail />} />
          <Route path="/extract" element={<ExtractMarket />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
