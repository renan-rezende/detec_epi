import { Outlet, NavLink } from 'react-router-dom'
import { Camera, PlusCircle, Shield, Activity } from 'lucide-react'
import './Layout.css'

export default function Layout() {
  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo">
            <Shield className="logo-icon" />
            <div className="logo-text">
              <span className="logo-title">EPI</span>
              <span className="logo-subtitle">Detection</span>
            </div>
          </div>
        </div>
        
        <nav className="nav-menu">
          <NavLink 
            to="/" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <Camera className="nav-icon" />
            <span>Monitoramento</span>
          </NavLink>
          
          <NavLink 
            to="/add-camera" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <PlusCircle className="nav-icon" />
            <span>Adicionar Câmera</span>
          </NavLink>
        </nav>
        
        <div className="sidebar-footer">
          <div className="status-indicator">
            <Activity className="status-icon pulse" />
            <span>Sistema Ativo</span>
          </div>
        </div>
      </aside>
      
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}

