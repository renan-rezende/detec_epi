import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import AddCamera from './pages/AddCamera'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="add-camera" element={<AddCamera />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App

