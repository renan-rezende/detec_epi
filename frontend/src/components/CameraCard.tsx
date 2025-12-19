import { useState } from 'react'
import { Video, VideoOff, Settings, Trash2, RefreshCw } from 'lucide-react'
import { Camera, cameraService } from '../services/api'
import './CameraCard.css'

interface CameraCardProps {
  camera: Camera
  onDelete: (id: string) => void
  onToggle: (id: string, active: boolean) => void
}

export default function CameraCard({ camera, onDelete, onToggle }: CameraCardProps) {
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)
  const [key, setKey] = useState(0)

  const handleImageLoad = () => {
    setIsLoading(false)
    setHasError(false)
  }

  const handleImageError = () => {
    setIsLoading(false)
    setHasError(true)
  }

  const handleRefresh = () => {
    setIsLoading(true)
    setHasError(false)
    setKey(prev => prev + 1)
  }

  const handleToggle = () => {
    onToggle(camera.id, !camera.active)
  }

  const handleDelete = () => {
    if (confirm(`Tem certeza que deseja remover a câmera "${camera.name}"?`)) {
      onDelete(camera.id)
    }
  }

  return (
    <div className={`camera-card ${!camera.active ? 'inactive' : ''}`}>
      <div className="card-header">
        <div className="camera-info">
          <h3 className="camera-name">{camera.name}</h3>
          <span className={`camera-status ${camera.active ? 'active' : 'inactive'}`}>
            {camera.active ? 'Ativa' : 'Inativa'}
          </span>
        </div>
        <div className="card-actions">
          <button 
            className="action-btn refresh" 
            onClick={handleRefresh}
            title="Recarregar stream"
          >
            <RefreshCw size={16} />
          </button>
          <button 
            className="action-btn toggle" 
            onClick={handleToggle}
            title={camera.active ? 'Desativar' : 'Ativar'}
          >
            {camera.active ? <VideoOff size={16} /> : <Video size={16} />}
          </button>
          <button 
            className="action-btn delete" 
            onClick={handleDelete}
            title="Remover câmera"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>

      <div className="video-container">
        {camera.active ? (
          <>
            {isLoading && (
              <div className="loading-overlay">
                <div className="loading-spinner"></div>
                <span>Conectando...</span>
              </div>
            )}
            {hasError ? (
              <div className="error-overlay">
                <VideoOff size={48} />
                <span>Erro ao carregar stream</span>
                <button className="retry-btn" onClick={handleRefresh}>
                  <RefreshCw size={16} />
                  Tentar novamente
                </button>
              </div>
            ) : (
              <img
                key={key}
                src={cameraService.getStreamUrl(camera.id)}
                alt={`Stream da câmera ${camera.name}`}
                className="video-stream"
                onLoad={handleImageLoad}
                onError={handleImageError}
              />
            )}
          </>
        ) : (
          <div className="inactive-overlay">
            <VideoOff size={48} />
            <span>Câmera desativada</span>
          </div>
        )}
      </div>

      <div className="card-footer">
        <div className="camera-meta">
          <span className="meta-item">
            <Settings size={14} />
            {camera.fps} FPS
          </span>
        </div>
      </div>
    </div>
  )
}

