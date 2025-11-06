import axios from 'axios'
import type {
  IniciarDebateRequest,
  IniciarDebateResponse,
  EstadoDebateResponse,
  ResultadoDebateResponse,
  HealthResponse,
} from '@/types/debate'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const debateApi = {
  iniciarDebate: async (request: IniciarDebateRequest): Promise<IniciarDebateResponse> => {
    const response = await api.post('/debate/iniciar', request)
    return response.data
  },

  ejecutarDebate: async (debateId: string): Promise<void> => {
    await api.post(`/debate/${debateId}/ejecutar`)
  },

  obtenerEstado: async (debateId: string): Promise<EstadoDebateResponse> => {
    const response = await api.get(`/debate/${debateId}/estado`)
    return response.data
  },

  obtenerResultado: async (debateId: string): Promise<ResultadoDebateResponse> => {
    const response = await api.get(`/debate/${debateId}/resultado`)
    return response.data
  },

  healthCheck: async (): Promise<HealthResponse> => {
    const response = await api.get('/health')
    return response.data
  },

  getStreamUrl: (debateId: string): string => {
    return `${API_BASE_URL}/api/v1/debate/${debateId}/stream`
  },
}

export default debateApi
