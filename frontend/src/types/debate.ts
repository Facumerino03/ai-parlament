// Request types
export interface IniciarDebateRequest {
  tema: string
  config?: {
    num_rondas?: number
    perspectivas?: string[]
    profundidad_rag?: number
  }
}

// Response types
export interface IniciarDebateResponse {
  debate_id: string
  status: string
  tema: string
  timestamp: string
}

export interface EstadoDebateResponse {
  debate_id: string
  tema: string
  fase_actual: string
  ronda_actual: number
  total_argumentos: number
  timestamp_inicio: string
  status: string
}

export interface ArgumentoType {
  id?: number
  agente: string
  rol: string
  contenido: string
  fase: string
  ronda: number
  timestamp: string
  referencias_rag?: string[]
  metadata?: Record<string, any>
}

export interface ResultadoDebateResponse {
  debate_id: string
  tema: string
  tema_reformulado?: string
  acta_completa: string
  consensos: string[]
  disensos: string[]
  propuestas_hibridas: string[]
  resumen_ejecutivo: string
  argumentos: ArgumentoType[]
  timestamp_inicio: string
  timestamp_fin?: string
  duracion_segundos?: number
  estadisticas?: Record<string, any>
}

export interface HealthResponse {
  status: string
  rag_initialized: boolean
  modelos_disponibles: string[]
  version?: string
}

// SSE Event types
export interface SSEArgumentoEvent {
  agente: string
  rol: string
  contenido: string
  fase: string
  ronda: number
  timestamp: string
  referencias_rag?: string[]
}

export interface SSEFaseCambioEvent {
  fase: string
  ronda: number
}

export interface SSECompletadoEvent {
  debate_id: string
  status: string
  total_argumentos?: number
}

// Agente information
export interface AgenteInfo {
  nombre: string
  rol: string
  color: string
  icon: string
}

// Debate phases
export enum DebateFase {
  INICIALIZACION = 'inicializacion',
  RONDA_INICIAL = 'ronda_inicial',
  DEBATE_LIBRE = 'debate_libre',
  INTERPELACIONES = 'interpelaciones',
  SINTESIS = 'sintesis',
  COMPLETADO = 'completado'
}

// Agent roles
export enum AgentRole {
  MODERADOR = 'moderador',
  ECONOMISTA = 'economista',
  SOCIOLOGO = 'sociologo',
  CIENTIFICO = 'cientifico',
  AMBIENTALISTA = 'ambientalista',
  ETICO = 'etico',
  PRAGMATICO = 'pragmatico',
  CRITICO = 'critico',
  SECRETARIO = 'secretario',
  ANALISTA_RAG = 'analista_rag',
  SINTETIZADOR = 'sintetizador'
}
