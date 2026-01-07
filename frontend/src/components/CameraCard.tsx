import { useState, useEffect, useCallback } from 'react'
import { Video, VideoOff, Settings, Trash2, RefreshCw, AlertTriangle, HardHat, Eye, Hand, Footprints, CheckCircle, Users, Shield } from 'lucide-react'
import { Camera, CameraAlerts, cameraService } from '../services/api'
import './CameraCard.css'

interface CameraCardProps {
  camera: Camera
  onDelete: (id: string) => void
  onToggle: (id: string, active: boolean) => void
}

// Mapeamento das classes de violação para informações de exibição
const VIOLATION_INFO: Record<number, { name: string; icon: React.ReactNode; shortName: string }> = {
  5: { name: 'Sem EPI', icon: <AlertTriangle size={16} />, shortName: 'Sem EPI' },
  7: { name: 'Sem Capacete', icon: <HardHat size={16} />, shortName: 'Capacete' },
  8: { name: 'Sem Óculos', icon: <Eye size={16} />, shortName: 'Óculos' },
  9: { name: 'Sem Luvas', icon: <Hand size={16} />, shortName: 'Luvas' },
  10: { name: 'Sem Botas', icon: <Footprints size={16} />, shortName: 'Botas' },
}

export default function CameraCard({ camera, onDelete, onToggle }: CameraCardProps) {
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)
  const [key, setKey] = useState(0)
  const [alerts, setAlerts] = useState<CameraAlerts | null>(null)

  // Função para buscar alertas
  const fetchAlerts = useCallback(async () => {
    if (!camera.active) return
    
    try {
      const data = await cameraService.getCameraAlerts(camera.id)
      // Debug: Log quando há violações
      if (data.has_violations) {
        console.log('🚨 Violações detectadas:', data.violations)
      }
      setAlerts(data)
    } catch (err) {
      // Silenciosamente ignora erros de polling
      console.debug('Erro ao buscar alertas:', err)
    }
  }, [camera.id, camera.active])

  // Polling de alertas a cada 500ms quando a câmera está ativa
  useEffect(() => {
    if (!camera.active) {
      setAlerts(null)
      return
    }

    // Buscar imediatamente
    fetchAlerts()

    // Configurar intervalo de polling
    const interval = setInterval(fetchAlerts, 500)

    return () => clearInterval(interval)
  }, [camera.active, fetchAlerts])

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

  // Agrupar violações por tipo e contar
  const getViolationCounts = () => {
    if (!alerts?.violations) return {}
    
    const counts: Record<number, number> = {}
    alerts.violations.forEach(v => {
      counts[v.class_id] = (counts[v.class_id] || 0) + 1
    })
    return counts
  }

  const violationCounts = getViolationCounts()
  const hasViolations = alerts?.has_violations || false

  return (
    <div className={`camera-card ${!camera.active ? 'inactive' : ''} ${hasViolations ? 'has-violations' : ''}`}>
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

      {/* Painel de Alertas de Violações */}
      {camera.active && (
        <div className={`alerts-panel ${hasViolations ? 'has-alerts' : 'no-alerts'}`}>
          <div className="alerts-header">
            {hasViolations ? (
              <>
                <AlertTriangle size={18} className="alert-icon danger" />
                <span className="alerts-title danger">Violações Detectadas</span>
              </>
            ) : (
              <>
                <CheckCircle size={18} className="alert-icon success" />
                <span className="alerts-title success">Conformidade OK</span>
              </>
            )}
          </div>

          {hasViolations && (
            <div className="violations-list">
              {Object.entries(violationCounts).map(([classId, count]) => {
                const info = VIOLATION_INFO[Number(classId)]
                // Mostrar mesmo se não estiver no mapeamento (com ícone padrão)
                const displayInfo = info || { 
                  name: `Classe ${classId}`, 
                  icon: <AlertTriangle size={16} />, 
                  shortName: `Violação ${classId}` 
                }
                return (
                  <div key={classId} className="violation-item">
                    <span className="violation-icon">{displayInfo.icon}</span>
                    <span className="violation-name">{displayInfo.shortName}</span>
                    <span className="violation-count">{count}x</span>
                  </div>
                )
              })}
            </div>
          )}

          <div className="alerts-stats">
            <div className="stat-item">
              <Users size={14} />
              <span>{alerts?.person_count || 0} Pessoas</span>
            </div>
            <div className="stat-item">
              <Shield size={14} />
              <span>{alerts?.epi_count || 0} EPIs</span>
            </div>
          </div>
        </div>
      )}

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

