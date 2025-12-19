import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Camera as CameraIcon, PlusCircle, RefreshCw, AlertTriangle } from 'lucide-react'
import { Camera, cameraService } from '../services/api'
import CameraCard from '../components/CameraCard'
import './Dashboard.css'

export default function Dashboard() {
  const [cameras, setCameras] = useState<Camera[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchCameras = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await cameraService.listCameras()
      setCameras(data)
    } catch (err) {
      setError('Erro ao carregar câmeras. Verifique se o servidor está rodando.')
      console.error('Erro ao carregar câmeras:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCameras()
  }, [])

  const handleDeleteCamera = async (id: string) => {
    try {
      await cameraService.deleteCamera(id)
      setCameras(prev => prev.filter(cam => cam.id !== id))
    } catch (err) {
      console.error('Erro ao deletar câmera:', err)
      alert('Erro ao remover câmera')
    }
  }

  const handleToggleCamera = async (id: string, active: boolean) => {
    try {
      const updated = await cameraService.updateCamera(id, { active } as any)
      setCameras(prev => prev.map(cam => cam.id === id ? updated : cam))
    } catch (err) {
      console.error('Erro ao atualizar câmera:', err)
      alert('Erro ao atualizar câmera')
    }
  }

  if (loading) {
    return (
      <div className="dashboard">
        <div className="dashboard-loading">
          <div className="loading-spinner large"></div>
          <span>Carregando câmeras...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1 className="page-title">
            <CameraIcon className="title-icon" />
            Monitoramento de EPIs
          </h1>
          <p className="page-subtitle">
            Visualize em tempo real as detecções de Equipamentos de Proteção Individual
          </p>
        </div>
        <div className="header-actions">
          <button className="btn btn-secondary" onClick={fetchCameras}>
            <RefreshCw size={18} />
            Atualizar
          </button>
          <Link to="/add-camera" className="btn btn-primary">
            <PlusCircle size={18} />
            Nova Câmera
          </Link>
        </div>
      </header>

      {error && (
        <div className="error-banner">
          <AlertTriangle size={20} />
          <span>{error}</span>
          <button className="retry-link" onClick={fetchCameras}>
            Tentar novamente
          </button>
        </div>
      )}

      {cameras.length === 0 && !error ? (
        <div className="empty-state">
          <div className="empty-icon">
            <CameraIcon size={64} />
          </div>
          <h2>Nenhuma câmera cadastrada</h2>
          <p>Adicione sua primeira câmera para começar o monitoramento</p>
          <Link to="/add-camera" className="btn btn-primary">
            <PlusCircle size={18} />
            Adicionar Câmera
          </Link>
        </div>
      ) : (
        <div className="cameras-grid">
          {cameras.map((camera, index) => (
            <div 
              key={camera.id} 
              className="camera-item"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <CameraCard
                camera={camera}
                onDelete={handleDeleteCamera}
                onToggle={handleToggleCamera}
              />
            </div>
          ))}
        </div>
      )}

      <div className="dashboard-stats">
        <div className="stat-card">
          <span className="stat-value">{cameras.length}</span>
          <span className="stat-label">Câmeras Total</span>
        </div>
        <div className="stat-card">
          <span className="stat-value success">
            {cameras.filter(c => c.active).length}
          </span>
          <span className="stat-label">Ativas</span>
        </div>
        <div className="stat-card">
          <span className="stat-value warning">
            {cameras.filter(c => !c.active).length}
          </span>
          <span className="stat-label">Inativas</span>
        </div>
      </div>
    </div>
  )
}

