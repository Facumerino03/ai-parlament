import { useState, useEffect, useRef } from 'react'
import debateApi from './services/api'
import type { ArgumentoType, AgenteInfo } from './types/debate'
import { cn, formatTimestamp, downloadTextFile } from './lib/utils'
import { Button } from './components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './components/ui/card'
import {
  Users, TrendingUp, Heart, FlaskConical, Leaf, Scale, Wrench, Search,
  FileText, Database, Lightbulb, Loader2, Download, CheckCircle2, AlertCircle
} from 'lucide-react'

// Agentes configuration
const AGENTES_INFO: Record<string, AgenteInfo> = {
  moderador: { nombre: 'Moderador', rol: 'Orquestación', color: 'bg-blue-500', icon: 'Users' },
  economista: { nombre: 'Economista', rol: 'Análisis Económico', color: 'bg-green-500', icon: 'TrendingUp' },
  sociologo: { nombre: 'Sociólogo', rol: 'Impacto Social', color: 'bg-purple-500', icon: 'Heart' },
  cientifico: { nombre: 'Científico', rol: 'Evidencia Empírica', color: 'bg-cyan-500', icon: 'FlaskConical' },
  ambientalista: { nombre: 'Ambientalista', rol: 'Sostenibilidad', color: 'bg-emerald-600', icon: 'Leaf' },
  etico: { nombre: 'Ético', rol: 'Dilemas Morales', color: 'bg-pink-500', icon: 'Scale' },
  pragmatico: { nombre: 'Pragmático', rol: 'Viabilidad Práctica', color: 'bg-orange-500', icon: 'Wrench' },
  critico: { nombre: 'Crítico', rol: 'Análisis Crítico', color: 'bg-red-500', icon: 'Search' },
  secretario: { nombre: 'Secretario', rol: 'Registro', color: 'bg-gray-500', icon: 'FileText' },
  analista_rag: { nombre: 'Analista', rol: 'Información', color: 'bg-indigo-500', icon: 'Database' },
  sintetizador: { nombre: 'Sintetizador', rol: 'Síntesis Final', color: 'bg-yellow-500', icon: 'Lightbulb' },
}

const getIcon = (iconName: string) => {
  const icons: Record<string, any> = {
    Users, TrendingUp, Heart, FlaskConical, Leaf, Scale, Wrench, Search, FileText, Database, Lightbulb
  }
  return icons[iconName] || Users
}

function App() {
  const [debateId, setDebateId] = useState<string | null>(null)
  const [tema, setTema] = useState('')
  const [isInitiating, setIsInitiating] = useState(false)
  const [argumentos, setArgumentos] = useState<ArgumentoType[]>([])
  const [fase, setFase] = useState('')
  const [ronda, setRonda] = useState(0)
  const [isStreaming, setIsStreaming] = useState(false)
  const [isCompleted, setIsCompleted] = useState(false)
  const [agenteActual, setAgenteActual] = useState<string | null>(null)
  const [consensos, setConsensos] = useState<string[]>([])
  const [resultado, setResultado] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const eventSourceRef = useRef<EventSource | null>(null)
  const argumentosEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to latest argument
  useEffect(() => {
    argumentosEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [argumentos])

  const iniciarDebate = async () => {
    if (!tema.trim()) return

    setError(null)
    setIsInitiating(true)

    try {
      // Iniciar debate
      const response = await debateApi.iniciarDebate({ tema })
      setDebateId(response.debate_id)

      // Ejecutar debate
      await debateApi.ejecutarDebate(response.debate_id)

      // Conectar SSE
      conectarStream(response.debate_id)
      setIsStreaming(true)
    } catch (err: any) {
      setError(err.message || 'Error al iniciar debate')
      setIsInitiating(false)
    }
  }

  const conectarStream = (id: string) => {
    const url = debateApi.getStreamUrl(id)
    console.log('🔌 Conectando a SSE stream:', url)
    const es = new EventSource(url)

    es.addEventListener('connected', (event) => {
      const data = JSON.parse(event.data)
      console.log('✅ Conexión SSE establecida:', data)
    })

    es.addEventListener('waiting', (event) => {
      const data = JSON.parse(event.data)
      console.log('⏳ Esperando:', data.mensaje)
    })

    es.addEventListener('ping', (event) => {
      const data = JSON.parse(event.data)
      console.log('🏓 Ping recibido:', data)
    })

    es.addEventListener('argumento', (event) => {
      console.log('📝 Evento argumento recibido:', event.data)
      try {
        const data = JSON.parse(event.data)
        console.log('📝 Argumento parseado:', data)
        setArgumentos(prev => [...prev, data])
        setAgenteActual(data.agente)
        setTimeout(() => setAgenteActual(null), 3000)
        setIsInitiating(false)
      } catch (err) {
        console.error('❌ Error parseando argumento:', err, event.data)
      }
    })

    es.addEventListener('fase_cambio', (event) => {
      const data = JSON.parse(event.data)
      console.log('🔄 Cambio de fase:', data)
      setFase(data.fase)
      setRonda(data.ronda || 0)
    })

    es.addEventListener('completado', async () => {
      console.log('✅ Debate completado')
      setIsCompleted(true)
      setIsStreaming(false)
      es.close()

      // Obtener resultado final
      if (id) {
        try {
          const res = await debateApi.obtenerResultado(id)
          console.log('📊 Resultado obtenido:', res)
          setResultado(res)
        } catch (err) {
          console.error('❌ Error obteniendo resultado:', err)
        }
      }
    })

    es.addEventListener('error', (event: any) => {
      console.error('❌ Error event recibido:', event)
      if (event.data) {
        try {
          const data = JSON.parse(event.data)
          setError(data.mensaje || 'Error en el debate')
        } catch {
          setError('Error en el debate')
        }
      }
    })

    es.onerror = (err) => {
      console.error('❌ EventSource error:', err)
      setError('Error en conexión de streaming')
      setIsStreaming(false)
      es.close()
    }

    es.onopen = () => {
      console.log('🌐 EventSource connection opened')
    }

    eventSourceRef.current = es
  }

  const descargarActa = () => {
    if (!resultado) return
    const content = `PARLAMENTO VIRTUAL DE DEBATES
================================

TEMA: ${resultado.tema}
FECHA: ${resultado.timestamp_inicio}

RESUMEN EJECUTIVO:
${resultado.resumen_ejecutivo}

CONSENSOS ALCANZADOS:
${resultado.consensos.map((c: string, i: number) => `${i + 1}. ${c}`).join('\n')}

DISENSOS REMANENTES:
${resultado.disensos.map((d: string, i: number) => `${i + 1}. ${d}`).join('\n')}

PROPUESTAS HÍBRIDAS:
${resultado.propuestas_hibridas.map((p: string, i: number) => `${i + 1}. ${p}`).join('\n')}

TRANSCRIPCIÓN COMPLETA:
================================

${resultado.acta_completa}
`
    downloadTextFile(content, `debate_${debateId}.txt`)
  }

  const nuevoDebate = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
    }
    setDebateId(null)
    setTema('')
    setArgumentos([])
    setFase('')
    setRonda(0)
    setIsCompleted(false)
    setIsStreaming(false)
    setResultado(null)
    setConsensos([])
    setError(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">
            🏛️ Parlamento Virtual de Debates
          </h1>
          <p className="text-slate-600">
            Análisis multidisciplinario con agentes de IA especializados
          </p>
        </div>

        {/* Status indicator */}
        {isStreaming && (
          <div className="fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-full shadow-lg flex items-center gap-2 animate-pulse">
            <div className="w-2 h-2 bg-white rounded-full animate-dot-pulse"></div>
            <span className="text-sm font-medium">Debate en curso...</span>
          </div>
        )}

        {/* Error message */}
        {error && (
          <Card className="mb-6 border-red-300 bg-red-50">
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-red-700">
                <AlertCircle className="h-5 w-5" />
                <span>{error}</span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Form or debate view */}
        {!debateId ? (
          <Card className="max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle>Iniciar Nuevo Debate</CardTitle>
              <CardDescription>
                Ingresa un tema complejo para que sea analizado desde múltiples perspectivas
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <textarea
                  className="w-full min-h-[120px] p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  placeholder="Ejemplo: ¿Debería implementarse una semana laboral de 4 días?"
                  value={tema}
                  onChange={(e) => setTema(e.target.value)}
                  maxLength={500}
                  disabled={isInitiating}
                />
                <div className="text-sm text-slate-500 mt-1">
                  {tema.length}/500 caracteres
                </div>
              </div>
              <Button
                onClick={iniciarDebate}
                disabled={!tema.trim() || isInitiating}
                className="w-full"
                size="lg"
              >
                {isInitiating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Iniciando debate...
                  </>
                ) : (
                  'Iniciar Debate'
                )}
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {/* Progress */}
            {fase && (
              <Card>
                <CardContent className="pt-6">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm text-slate-600">
                      <span>Fase: {fase.replace('_', ' ').toUpperCase()}</span>
                      {ronda > 0 && <span>Ronda {ronda}</span>}
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${(argumentos.length / 30) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Agentes Grid */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Agentes Participantes</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                  {Object.entries(AGENTES_INFO).map(([key, agente]) => {
                    const Icon = getIcon(agente.icon)
                    const isHablando = agenteActual === key
                    return (
                      <div
                        key={key}
                        className={cn(
                          "p-3 rounded-lg border-2 transition-all duration-300",
                          isHablando
                            ? `${agente.color} border-current shadow-lg scale-105 animate-pulse-border`
                            : "border-slate-200 bg-white"
                        )}
                      >
                        <div className="flex flex-col items-center text-center gap-2">
                          <div className={cn(
                            "p-2 rounded-full",
                            isHablando ? "bg-white/20" : agente.color
                          )}>
                            <Icon className={cn(
                              "h-5 w-5",
                              isHablando ? "text-white" : "text-white"
                            )} />
                          </div>
                          <div>
                            <div className={cn(
                              "font-semibold text-xs",
                              isHablando ? "text-white" : "text-slate-900"
                            )}>
                              {agente.nombre}
                            </div>
                            <div className={cn(
                              "text-xs",
                              isHablando ? "text-white/80" : "text-slate-500"
                            )}>
                              {agente.rol}
                            </div>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Stream de Argumentos */}
            <Card>
              <CardHeader>
                <CardTitle>Debate en Vivo</CardTitle>
                <CardDescription>
                  {argumentos.length === 0 && isStreaming && (
                    <span className="text-blue-600 animate-pulse">
                      Esperando argumentos del debate...
                    </span>
                  )}
                  {argumentos.length > 0 && (
                    <span className="text-slate-600">
                      {argumentos.length} intervenciones registradas
                    </span>
                  )}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
                  {argumentos.length === 0 && isStreaming && (
                    <div className="text-center py-12">
                      <Loader2 className="h-12 w-12 animate-spin mx-auto text-blue-500 mb-4" />
                      <p className="text-slate-600 font-medium">Preparando el debate...</p>
                      <p className="text-slate-500 text-sm mt-2">Los agentes están analizando el tema</p>
                    </div>
                  )}
                  {argumentos.map((arg, idx) => {
                    const agenteInfo = AGENTES_INFO[arg.agente] || AGENTES_INFO.moderador
                    const Icon = getIcon(agenteInfo.icon)
                    return (
                      <div
                        key={idx}
                        className="bg-slate-50 rounded-lg p-4 border border-slate-200 animate-slide-in-up"
                      >
                        <div className="flex items-start gap-3">
                          <div className={cn("p-2 rounded-full shrink-0", agenteInfo.color)}>
                            <Icon className="h-4 w-4 text-white" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between mb-2">
                              <div>
                                <span className="font-semibold text-slate-900">
                                  {agenteInfo.nombre}
                                </span>
                                <span className="text-sm text-slate-500 ml-2">
                                  {arg.rol}
                                </span>
                              </div>
                              <span className="text-xs text-slate-400">
                                {formatTimestamp(arg.timestamp)}
                              </span>
                            </div>
                            <p className="text-slate-700 whitespace-pre-wrap leading-relaxed">
                              {arg.contenido}
                            </p>
                            {arg.ronda > 0 && (
                              <div className="mt-2">
                                <span className="inline-block px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded">
                                  Ronda {arg.ronda}
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    )
                  })}
                  <div ref={argumentosEndRef} />
                </div>
              </CardContent>
            </Card>

            {/* Resultado Final */}
            {isCompleted && resultado && (
              <Card className="border-green-300 bg-green-50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CheckCircle2 className="h-6 w-6 text-green-600" />
                    Debate Completado
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h3 className="font-semibold text-lg mb-2">Resumen Ejecutivo:</h3>
                    <p className="text-slate-700">{resultado.resumen_ejecutivo}</p>
                  </div>

                  {resultado.consensos.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-lg mb-2">Consensos:</h3>
                      <ul className="list-disc list-inside space-y-1">
                        {resultado.consensos.map((c: string, i: number) => (
                          <li key={i} className="text-slate-700">{c}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {resultado.propuestas_hibridas.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-lg mb-2">Propuestas:</h3>
                      <ul className="list-disc list-inside space-y-1">
                        {resultado.propuestas_hibridas.map((p: string, i: number) => (
                          <li key={i} className="text-slate-700">{p}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="flex gap-3 pt-4">
                    <Button onClick={descargarActa} variant="outline">
                      <Download className="mr-2 h-4 w-4" />
                      Descargar Acta
                    </Button>
                    <Button onClick={nuevoDebate}>
                      Nuevo Debate
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default App
