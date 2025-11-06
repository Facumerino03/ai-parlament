# AI Parliament Backend

Backend del sistema de Parlamento Virtual de Debates - Un sistema donde múltiples agentes de IA especializados debaten sobre problemáticas complejas desde diferentes perspectivas para generar análisis balanceados y conclusiones fundamentadas.

## 📋 Características

- **11 Agentes Especializados**: Moderador, Economista, Sociólogo, Científico, Ambientalista, Ético, Pragmático, Crítico, Secretario, Analista RAG, Sintetizador
- **Sistema RAG**: Base de conocimiento vectorial con ChromaDB para fundamentar argumentos
- **API REST**: Endpoints para crear y gestionar debates
- **Streaming en Tiempo Real**: Server-Sent Events para seguir debates en vivo
- **LLMs Gratuitos**: Usa Google Gemini Flash 1.5 y Meta Llama 3.1 vía OpenRouter

## 🏗️ Arquitectura

```
backend/
├── main.py                 # Punto de entrada
├── requirements.txt        # Dependencias
├── .env                   # Variables de entorno (crear desde .env.example)
├── app/
│   ├── api/               # Endpoints REST
│   ├── core/              # Lógica central (orquestador, config, estado)
│   ├── agents/            # 11 agentes especializados
│   ├── llm/               # Cliente LLM y prompts
│   └── rag/               # Sistema RAG (vector store, embeddings, retriever)
└── tests/                 # Tests
```

## 📦 Requisitos

- **Python**: 3.10 o superior
- **OpenRouter API Key**: Gratuita en [https://openrouter.ai/](https://openrouter.ai/)
- **Espacio en Disco**: ~2GB para ChromaDB
- **RAM**: Mínimo 4GB recomendado

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
git clone <repo-url>
cd ai-parlament/backend
```

### 2. Crear Entorno Virtual

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env y añadir tu API key de OpenRouter
nano .env  # o tu editor preferido
```

**Contenido mínimo de `.env`:**
```env
OPENROUTER_API_KEY=tu_api_key_aqui
```

### 5. Obtener API Key de OpenRouter

1. Visita [https://openrouter.ai/](https://openrouter.ai/)
2. Crea una cuenta (gratis)
3. Ve a "Keys" y genera una nueva API key
4. Copia la key y pégala en tu archivo `.env`

## ▶️ Ejecución

### Iniciar el Servidor

```bash
python main.py
```

El servidor se iniciará en `http://localhost:8000`

### Verificar que Funciona

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Ver documentación interactiva
# Abre en tu navegador: http://localhost:8000/docs
```

## 📚 Uso de la API

### 1. Iniciar un Debate

```bash
curl -X POST http://localhost:8000/api/v1/debate/iniciar \
  -H "Content-Type: application/json" \
  -d '{
    "tema": "¿Debería implementarse una semana laboral de 4 días?",
    "config": {
      "num_rondas": 5
    }
  }'
```

**Respuesta:**
```json
{
  "debate_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "iniciado",
  "tema": "¿Debería implementarse una semana laboral de 4 días?",
  "timestamp": "2024-11-06T10:30:00Z"
}
```

### 2. Ejecutar el Debate

```bash
curl -X POST http://localhost:8000/api/v1/debate/{debate_id}/ejecutar
```

### 3. Seguir en Tiempo Real (SSE)

```bash
curl -N http://localhost:8000/api/v1/debate/{debate_id}/stream
```

O en tu navegador/frontend, usa EventSource:

```javascript
const eventSource = new EventSource('http://localhost:8000/api/v1/debate/{debate_id}/stream');

eventSource.addEventListener('argumento', (event) => {
  const argumento = JSON.parse(event.data);
  console.log(`[${argumento.agente}]: ${argumento.contenido}`);
});

eventSource.addEventListener('completado', (event) => {
  console.log('Debate completado!');
  eventSource.close();
});
```

### 4. Obtener Resultado Final

```bash
curl http://localhost:8000/api/v1/debate/{debate_id}/resultado
```

**Respuesta incluye:**
- Acta completa del debate
- Consensos identificados
- Disensos remanentes
- Propuestas híbridas
- Resumen ejecutivo
- Todos los argumentos con metadatos

## 🔍 Endpoints Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/debate/iniciar` | Crear nuevo debate |
| POST | `/api/v1/debate/{id}/ejecutar` | Ejecutar debate |
| GET | `/api/v1/debate/{id}/stream` | Stream en tiempo real (SSE) |
| GET | `/api/v1/debate/{id}/estado` | Estado actual del debate |
| GET | `/api/v1/debate/{id}/resultado` | Resultado final (solo si completado) |
| GET | `/api/v1/debates` | Listar todos los debates |
| DELETE | `/api/v1/debate/{id}` | Eliminar debate de memoria |
| GET | `/api/v1/health` | Health check del sistema |

### Documentación Interactiva

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🤖 Los 11 Agentes

### Agentes de Perspectiva

1. **Moderador**: Orquesta el debate, asigna turnos, identifica consensos
2. **Economista**: Analiza viabilidad financiera, costos, beneficios
3. **Sociólogo**: Impacto social, equidad, bienestar comunitario
4. **Científico**: Evidencia empírica, datos duros, viabilidad técnica
5. **Ambientalista**: Impacto ecológico, sostenibilidad
6. **Ético**: Implicaciones morales, dilemas éticos
7. **Pragmático**: Implementación práctica, viabilidad real
8. **Crítico**: Cuestiona supuestos, identifica falacias

### Agentes de Soporte

9. **Secretario**: Registra intervenciones, genera actas
10. **Analista RAG**: Busca información en la base de conocimiento
11. **Sintetizador**: Genera conclusiones finales y consensos

## 📊 Sistema RAG

El sistema RAG (Retrieval-Augmented Generation) permite a los agentes fundamentar sus argumentos con información de una base de conocimiento.

### Categorías de Documentos

- **estudios/**: Papers académicos y estudios de investigación
- **estadisticas/**: Datos y cifras verificables
- **casos_historicos/**: Implementaciones previas documentadas
- **falacias/**: Guía de falacias lógicas comunes

### Agregar Documentos

1. Coloca archivos `.txt` o `.md` en `app/rag/data/{categoria}/`
2. Reinicia el servidor (o la próxima vez que se inicialice se cargarán)

Los documentos se indexan automáticamente con embeddings y se almacenan en ChromaDB.

## ⚙️ Configuración Avanzada

### Variables de Entorno

Puedes personalizar en `.env`:

```env
# LLM
OPENROUTER_API_KEY=tu_key
MODEL_GEMINI=google/gemini-flash-1.5
MODEL_LLAMA=meta-llama/llama-3.1-8b-instruct

# Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=True

# RAG
CHROMA_PERSIST_DIR=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
RAG_TOP_K=5

# Debate
DEFAULT_ROUNDS=5
MAX_TOKENS_PER_ARGUMENT=500
TEMPERATURE_DEFAULT=0.7

# Rate Limiting
API_CALL_DELAY=0.5
MAX_RETRIES=3
```

### Modelos LLM

Por defecto usa modelos gratuitos/baratos de OpenRouter:

- **Gemini Flash 1.5**: Moderador, Economista, Ético, Analista RAG, Sintetizador
- **Llama 3.1 8B**: Otros agentes

Puedes cambiar los modelos en `app/core/config.py` en `AGENT_MODELS`.

## 🧪 Testing

```bash
# Ejecutar tests básicos
python -m pytest tests/

# Con cobertura
python -m pytest --cov=app tests/
```

## 📝 Logs

Los logs se guardan en:
- **Consola**: Output en tiempo real
- **Archivo**: `backend.log`

Nivel de logging configurableclase con `DEBUG=True/False` en `.env`.

## 🐛 Troubleshooting

### Error: "OpenRouter API key is required"

- Verifica que `.env` existe y contiene `OPENROUTER_API_KEY`
- La API key debe ser válida

### Error: "ChromaDB no inicializa"

- Asegúrate de tener suficiente espacio en disco
- Verifica permisos de escritura en el directorio del proyecto
- Elimina `./chroma_db/` y reinicia

### Puerto 8000 ocupado

Cambia el puerto en `.env`:
```env
PORT=8080
```

### Rate Limits de OpenRouter

Si recibes errores 429:
- Aumenta `API_CALL_DELAY` en `.env`
- Los modelos gratuitos tienen límites generosos pero existen
- Considera usar API key con créditos si necesitas mayor throughput

## 📊 Performance

- **Debate típico (5 rondas, 7 agentes)**: ~2-5 minutos
- **Argumentos generados**: ~25-35
- **Tokens consumidos**: ~15,000-25,000
- **Costo con modelos gratuitos**: $0.00

## 🔐 Consideraciones de Seguridad

- **API Keys**: Nunca subas tu `.env` al repositorio
- **CORS**: Configurado para localhost por defecto
- **Rate Limiting**: Implementado a nivel de cliente LLM
- **Validación**: Todos los inputs validados con Pydantic

## 🚧 Limitaciones Conocidas

- **Estado en Memoria**: Los debates se pierden al reiniciar el servidor (se puede implementar persistencia con Redis/DB)
- **Concurrencia**: Limitada a ~10 debates simultáneos (configurable)
- **Context Length**: Debates muy largos pueden exceder límites de contexto del LLM

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## 📄 Licencia

[Especificar licencia]

## 📧 Contacto

[Información de contacto]

## 🙏 Agradecimientos

- OpenRouter por acceso a LLMs gratuitos
- Sentence-Transformers por embeddings de calidad
- ChromaDB por vector store eficiente

---

**Versión**: 1.0.0
**Última actualización**: 2024-11-06
