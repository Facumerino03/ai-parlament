# AI Parliament Backend

Backend del sistema de Parlamento Virtual de Debates - Un sistema donde múltiples agentes de IA especializados debaten sobre problemáticas complejas desde diferentes perspectivas para generar análisis balanceados y conclusiones fundamentadas.

## 📋 Características

- **11 Agentes Especializados**: Moderador, Economista, Sociólogo, Científico, Ambientalista, Ético, Pragmático, Crítico, Secretario, Analista RAG, Sintetizador
- **Sistema RAG**: Base de conocimiento vectorial con ChromaDB para fundamentar argumentos
- **API REST**: Endpoints para crear y gestionar debates
- **Streaming en Tiempo Real**: Server-Sent Events para seguir debates en vivo
- **LLMs Potentes y Rápidos**: Llama 3.3 70B y Llama 3.1 8B vía Groq API (gratuito)

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

- **Python**: 3.10, 3.11 o 3.12 (⚠️ **NO usar 3.13+**, tiene incompatibilidades con dependencias)
- **Groq API Key**: Gratuita en [https://console.groq.com/](https://console.groq.com/)
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

# Editar .env y añadir tu API key de Groq
nano .env  # o tu editor preferido
```

**Contenido mínimo de `.env`:**
```env
OPENROUTER_API_KEY=gsk_tu_groq_api_key_aqui
OPENROUTER_BASE_URL=https://api.groq.com/openai/v1
MODEL_GEMINI=llama-3.3-70b-versatile
MODEL_LLAMA=llama-3.1-8b-instant
```

**Nota:** La variable se llama `OPENROUTER_API_KEY` por compatibilidad con el código, pero usa tu Groq API key.

### 5. Obtener API Key de Groq

1. Visita [https://console.groq.com/](https://console.groq.com/)
2. Crea una cuenta (gratis)
3. Ve a "API Keys" y genera una nueva key
4. Copia la key (empieza con `gsk_`) y pégala en tu archivo `.env`

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

**Formatos soportados:** `.txt` y `.md`

#### Método 1: Agregar y Reiniciar (Recomendado)

1. **Crear archivo** en la carpeta correspondiente:
```bash
# Ejemplos:
backend/app/rag/data/estudios/mi_estudio.txt
backend/app/rag/data/estadisticas/datos_nuevos.md
backend/app/rag/data/casos_historicos/caso_historico.txt
backend/app/rag/data/falacias/nueva_falacia.md
```

2. **Eliminar base de datos** para forzar recarga:
```bash
# Desde la raíz del proyecto
rm -rf backend/chroma_db
```

3. **Reiniciar el backend** - se indexan automáticamente:
```bash
cd backend
python main.py
```

Los logs mostrarán:
```
INFO: Loaded document: mi_estudio.txt
INFO: Total documents loaded: 8
```

#### Formato Recomendado para Documentos

**Estudios:**
```
Estudio: [Título]

Fuente: [Institución/Autores]
Año: [2024]

Metodología: [Descripción]

Resultados Clave:
1. [Resultado con datos concretos]
2. [Resultado con porcentajes]

Conclusiones: [Conclusión principal]
```

**Estadísticas:**
```
Estadísticas: [Tema]

Fuente: [Organización]
Año: [2024]

Datos:
- Métrica 1: XX%
- Métrica 2: $XX millones
- Métrica 3: XX personas

Contexto: [Explicación breve]
```

Los documentos se indexan automáticamente con embeddings y se almacenan en ChromaDB.

## ⚙️ Configuración Avanzada

### Variables de Entorno

Puedes personalizar en `.env`:

```env
# Groq API
OPENROUTER_API_KEY=gsk_tu_groq_api_key
OPENROUTER_BASE_URL=https://api.groq.com/openai/v1

# LLM Models (Groq)
MODEL_GEMINI=llama-3.3-70b-versatile
MODEL_LLAMA=llama-3.1-8b-instant

# Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=False

# RAG
CHROMA_PERSIST_DIR=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
RAG_TOP_K=5

# Debate
DEFAULT_ROUNDS=3
MAX_TOKENS_PER_ARGUMENT=180
TEMPERATURE_DEFAULT=0.7

# Rate Limiting (Groq: 1K RPM para 70b, 14.4K RPM para 8b)
API_CALL_DELAY=2.5
MAX_RETRIES=2
```

### Modelos LLM

Usa modelos de Groq (gratuitos y ultra-rápidos):

- **Llama 3.3 70B Versatile**: Moderador, Economista, Ético, Analista RAG, Sintetizador (agentes complejos)
- **Llama 3.1 8B Instant**: Sociólogo, Científico, Ambientalista, Pragmático, Crítico, Secretario (agentes rápidos)

**Límites de Groq:**
- llama-3.3-70b-versatile: 1,000 RPM (30 RPD)
- llama-3.1-8b-instant: 14,400 RPM (14,400 RPD)

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

### Error con Python 3.13+

**Problema:** Errores durante `pip install` o al importar dependencias

**Síntomas:**
```
ERROR: Could not build wheels for hnswlib, chroma-hnswlib
error: Microsoft Visual C++ 14.0 or greater is required
```

**Solución:**
1. Verifica tu versión de Python:
```bash
python --version
```

2. Si usás Python 3.13+, **desinstalalo** e instalá Python 3.12:
   - Descargá desde [python.org/downloads](https://www.python.org/downloads/)
   - Instalá Python 3.12.x
   - Recreá el entorno virtual con Python 3.12

3. Crea nuevo entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Por qué:** ChromaDB (especialmente `hnswlib` y `chroma-hnswlib`) aún no soporta Python 3.13 debido a cambios en la API de C.

### Error: "OpenRouter API key is required"

- Verifica que `.env` existe y contiene `OPENROUTER_API_KEY` con tu Groq API key
- La API key debe empezar con `gsk_` (formato de Groq)
- Verifica que `OPENROUTER_BASE_URL=https://api.groq.com/openai/v1`

### Error: "ChromaDB no inicializa"

- Asegúrate de tener suficiente espacio en disco
- Verifica permisos de escritura en el directorio del proyecto
- Elimina `./chroma_db/` y reinicia

### Puerto 8000 ocupado

Cambia el puerto en `.env`:
```env
PORT=8080
```

### Rate Limits de Groq

Si recibes errores 429 (Too Many Requests):
- Aumenta `API_CALL_DELAY` en `.env` (default: 2.5s)
- Verifica que no estés excediendo 1K RPM para el modelo 70b
- Considera reducir `DEFAULT_ROUNDS` a 2 si es necesario

### Error: "model_decommissioned"

- Verifica que estés usando modelos actuales de Groq
- Modelos válidos: `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`
- Consulta [https://console.groq.com/docs/models](https://console.groq.com/docs/models)
