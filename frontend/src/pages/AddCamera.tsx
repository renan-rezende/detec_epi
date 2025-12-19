import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  PlusCircle, 
  Camera, 
  Link as LinkIcon, 
  Gauge, 
  Tag,
  AlertCircle,
  CheckCircle,
  Trash2
} from 'lucide-react'
import { cameraService, Camera as CameraType } from '../services/api'
import './AddCamera.css'

export default function AddCamera() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    name: '',
    url: '',
    fps: 5
  })
  const [existingCameras, setExistingCameras] = useState<CameraType[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [nameExists, setNameExists] = useState(false)

  useEffect(() => {
    fetchCameras()
  }, [])

  useEffect(() => {
    // Verificar se o nome já existe
    const exists = existingCameras.some(
      cam => cam.name.toLowerCase() === formData.name.toLowerCase()
    )
    setNameExists(exists)
  }, [formData.name, existingCameras])

  const fetchCameras = async () => {
    try {
      const cameras = await cameraService.listCameras()
      setExistingCameras(cameras)
    } catch (err) {
      console.error('Erro ao carregar câmeras:', err)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'fps' ? parseInt(value) || 1 : value
    }))
    setError(null)
    setSuccess(null)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (nameExists) {
      setError(`Já existe uma câmera com o nome "${formData.name}"`)
      return
    }

    if (!formData.name.trim()) {
      setError('O nome da câmera é obrigatório')
      return
    }

    if (!formData.url.trim()) {
      setError('O link da câmera/vídeo é obrigatório')
      return
    }

    try {
      setLoading(true)
      setError(null)
      
      await cameraService.createCamera({
        name: formData.name.trim(),
        url: formData.url.trim(),
        fps: formData.fps
      })

      setSuccess(`Câmera "${formData.name}" adicionada com sucesso!`)
      setFormData({ name: '', url: '', fps: 5 })
      fetchCameras()

      // Redirecionar após 2 segundos
      setTimeout(() => {
        navigate('/')
      }, 2000)
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Erro ao adicionar câmera'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteCamera = async (id: string, name: string) => {
    if (!confirm(`Tem certeza que deseja remover a câmera "${name}"?`)) {
      return
    }

    try {
      await cameraService.deleteCamera(id)
      fetchCameras()
    } catch (err) {
      console.error('Erro ao remover câmera:', err)
      alert('Erro ao remover câmera')
    }
  }

  return (
    <div className="add-camera-page">
      <header className="page-header">
        <div className="header-content">
          <h1 className="page-title">
            <PlusCircle className="title-icon" />
            Adicionar Câmera
          </h1>
          <p className="page-subtitle">
            Cadastre uma nova câmera ou stream de vídeo para monitoramento
          </p>
        </div>
      </header>

      <div className="content-grid">
        <div className="form-section">
          <form onSubmit={handleSubmit} className="camera-form">
            <div className="form-group">
              <label htmlFor="name" className="form-label">
                <Tag size={18} />
                Nome da Câmera
              </label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="Ex: Entrada Principal"
                className={`form-input ${nameExists ? 'error' : ''}`}
              />
              {nameExists && (
                <span className="input-error">
                  <AlertCircle size={14} />
                  Este nome já está em uso
                </span>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="url" className="form-label">
                <LinkIcon size={18} />
                Link da Câmera / Vídeo
              </label>
              <input
                type="text"
                id="url"
                name="url"
                value={formData.url}
                onChange={handleInputChange}
                placeholder="rtsp://... ou caminho do arquivo de vídeo"
                className="form-input"
              />
              <span className="input-hint">
                Suporta RTSP, HTTP streams, arquivos de vídeo locais ou webcam (0, 1, etc.)
              </span>
            </div>

            <div className="form-group">
              <label htmlFor="fps" className="form-label">
                <Gauge size={18} />
                Taxa de Detecção (FPS)
              </label>
              <div className="slider-container">
                <input
                  type="range"
                  id="fps"
                  name="fps"
                  min="1"
                  max="30"
                  value={formData.fps}
                  onChange={handleInputChange}
                  className="form-slider"
                />
                <span className="slider-value">{formData.fps} FPS</span>
              </div>
              <span className="input-hint">
                Valores mais baixos consomem menos recursos. Recomendado: 5-10 FPS
              </span>
            </div>

            {error && (
              <div className="form-message error">
                <AlertCircle size={18} />
                {error}
              </div>
            )}

            {success && (
              <div className="form-message success">
                <CheckCircle size={18} />
                {success}
              </div>
            )}

            <button 
              type="submit" 
              className="submit-btn"
              disabled={loading || nameExists}
            >
              {loading ? (
                <>
                  <div className="btn-spinner"></div>
                  Adicionando...
                </>
              ) : (
                <>
                  <Camera size={18} />
                  Adicionar Câmera
                </>
              )}
            </button>
          </form>
        </div>

        <div className="cameras-section">
          <h2 className="section-title">
            <Camera size={20} />
            Câmeras Cadastradas
          </h2>
          
          {existingCameras.length === 0 ? (
            <div className="no-cameras">
              <Camera size={32} />
              <span>Nenhuma câmera cadastrada</span>
            </div>
          ) : (
            <ul className="cameras-list">
              {existingCameras.map((camera, index) => (
                <li 
                  key={camera.id} 
                  className="camera-item"
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  <div className="camera-info">
                    <span className="camera-name">{camera.name}</span>
                    <span className="camera-fps">{camera.fps} FPS</span>
                  </div>
                  <button
                    className="delete-btn"
                    onClick={() => handleDeleteCamera(camera.id, camera.name)}
                    title="Remover câmera"
                  >
                    <Trash2 size={16} />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}

