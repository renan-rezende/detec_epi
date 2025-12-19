import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

export interface Camera {
  id: string
  name: string
  url: string
  fps: number
  active: boolean
}

export interface CameraCreate {
  name: string
  url: string
  fps: number
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const cameraService = {
  // Listar todas as câmeras
  async listCameras(): Promise<Camera[]> {
    const response = await api.get('/api/cameras/')
    return response.data
  },

  // Obter câmera por ID
  async getCamera(id: string): Promise<Camera> {
    const response = await api.get(`/api/cameras/${id}`)
    return response.data
  },

  // Criar nova câmera
  async createCamera(camera: CameraCreate): Promise<Camera> {
    const response = await api.post('/api/cameras/', camera)
    return response.data
  },

  // Atualizar câmera
  async updateCamera(id: string, camera: Partial<CameraCreate>): Promise<Camera> {
    const response = await api.put(`/api/cameras/${id}`, camera)
    return response.data
  },

  // Deletar câmera
  async deleteCamera(id: string): Promise<void> {
    await api.delete(`/api/cameras/${id}`)
  },

  // Listar nomes das câmeras
  async listCameraNames(): Promise<string[]> {
    const response = await api.get('/api/cameras/names/list')
    return response.data
  },

  // Obter URL do stream
  getStreamUrl(cameraId: string): string {
    return `${API_BASE_URL}/api/stream/${cameraId}`
  },

  // Parar stream
  async stopStream(cameraId: string): Promise<void> {
    await api.post(`/api/stream/${cameraId}/stop`)
  },

  // Status do stream
  async getStreamStatus(cameraId: string): Promise<{ streaming: boolean; active: boolean }> {
    const response = await api.get(`/api/stream/${cameraId}/status`)
    return response.data
  },
}

export default api

