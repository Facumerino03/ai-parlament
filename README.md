# 🏛️ AI Parliament - Parlamento Virtual de Debates

Sistema completo de debates multidisciplinarios donde 11 agentes de IA especializados analizan temas complejos desde diferentes perspectivas para generar conclusiones balanceadas y fundamentadas.

## 🎯 ¿Qué es AI Parliament?

Un sistema que simula un parlamento donde múltiples agentes de IA debaten sobre problemáticas complejas desde perspectivas especializadas (económica, social, científica, ambiental, ética, pragmática, crítica), generando análisis integrales que una sola perspectiva no podría ofrecer.

**NO es** sobre política partidaria ni leyes, sino sobre **análisis multidisciplinario de problemáticas generales**.

## ✨ Características Principales

- 🤖 **11 Agentes Especializados** con perspectivas únicas
- 📚 **Sistema RAG** con base de conocimiento para fundamentar argumentos
- 🔴 **Streaming en Tiempo Real** para visualizar debates conforme ocurren
- 📊 **Identificación Automática** de consensos, disensos y propuestas híbridas
- 📄 **Generación de Actas** formales con transcripción completa
- 🎨 **Interfaz Moderna** y responsive con visualización tipo hemiciclo
- 💰 **Modelos Gratuitos y Ultra-Rápidos** (Llama 3.3 70B + Llama 3.1 8B vía Groq)

## 🎬 Demo Rápido

```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tu GROQ_API_KEY (empieza con gsk_)
python main.py

# Terminal 2: Frontend
cd frontend
npm install
npm run dev

# Abrir http://localhost:5173
```

**Tema de ejemplo:** "¿Debería implementarse una semana laboral de 4 días?"

## 🏗️ Arquitectura

### Backend (Python)
- **FastAPI** para API REST
- **ChromaDB** para vector store y RAG
- **Groq API** para acceso ultra-rápido a LLMs (Llama 3.3 70B + Llama 3.1 8B)
- **Sentence-Transformers** para embeddings
- **Server-Sent Events** para streaming en tiempo real

### Frontend (React + TypeScript)
- **React 18** + **TypeScript**
- **Vite** como build tool
- **Tailwind CSS** + **shadcn/ui**
- **Axios** para HTTP
- **EventSource** para SSE

```
ai-parlament/
├── backend/          # Python FastAPI server
│   ├── app/
│   │   ├── agents/   # 11 agentes especializados
│   │   ├── api/      # REST endpoints
│   │   ├── core/     # Orquestador y estado
│   │   ├── llm/      # Cliente LLM (Groq)
│   │   └── rag/      # Sistema RAG + documentos
│   ├── tests/
│   ├── main.py
│   └── requirements.txt
│
└── frontend/         # React TypeScript app
    ├── src/
    │   ├── components/
    │   ├── services/
    │   ├── types/
    │   ├── App.tsx
    │   └── main.tsx
    ├── package.json
    └── vite.config.ts
```

## 🤖 Los 11 Agentes

### Agentes de Perspectiva

1. **Moderador** 🔵 - Orquesta el debate, asigna turnos, identifica consensos
2. **Economista** 🟢 - Analiza viabilidad financiera, costos, beneficios
3. **Sociólogo** 🟣 - Impacto social, equidad, bienestar comunitario
4. **Científico** 🔵 - Evidencia empírica, datos duros, viabilidad técnica
5. **Ambientalista** 🟢 - Impacto ecológico, sostenibilidad
6. **Ético** 🔴 - Implicaciones morales, dilemas éticos
7. **Pragmático** 🟠 - Implementación práctica, viabilidad real
8. **Crítico** 🔴 - Cuestiona supuestos, identifica falacias

### Agentes de Soporte

9. **Secretario** ⚪ - Registra intervenciones, genera actas
10. **Analista RAG** 🔵 - Busca información en la base de conocimiento
11. **Sintetizador** 🟡 - Genera conclusiones finales y consensos

## 🔄 Flujo de un Debate

1. **Inicialización**
   - Usuario envía tema desde frontend
   - Moderador analiza y reformula
   - Analista RAG busca contexto inicial

2. **Ronda Inicial**
   - Cada agente presenta su postura inicial
   - Fundamentan con información del RAG

3. **Debate Libre** (3 rondas)
   - Agentes responden entre sí directamente
   - Moderador identifica puntos de tensión
   - Crítico señala falacias cuando detecta errores lógicos

4. **Síntesis**
   - Sintetizador analiza todo el debate
   - Identifica consensos y disensos
   - Propone soluciones híbridas

5. **Resultado**
   - Acta completa descargable
   - Resumen ejecutivo
   - Conclusiones balanceadas

## 🚀 Instalación Completa

### Requisitos Previos

- **Python 3.10 - 3.12** (⚠️ Python 3.13+ no es compatible por dependencias)
- Node.js 18+
- Groq API Key (gratuita en https://console.groq.com/)

### Backend Setup

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar API key
cp .env.example .env
# Editar .env y añadir tu Groq API key (empieza con gsk_)

# Iniciar servidor
python main.py
```

Backend disponible en: **http://localhost:8000**

### Frontend Setup

```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar desarrollo
npm run dev
```

Frontend disponible en: **http://localhost:5173**

## 📖 Documentación Detallada

- [Backend README](./backend/README.md) - Instalación, configuración, API
- [Frontend README](./frontend/README.md) - Setup, componentes, troubleshooting
- [Backend CHECKLIST](./backend/CHECKLIST.md) - Verificación de implementación

## 🎯 Casos de Uso

### Estudiantes
Analizar dilemas éticos, temas de debate académico

### Emprendedores
Evaluar decisiones de negocio desde múltiples ángulos

### Investigadores
Explorar temas multidisciplinarios con perspectivas diversas

### Toma de Decisiones
Obtener análisis balanceados para decisiones importantes

## 🌟 Ejemplos de Temas

- "¿Debería implementarse una semana laboral de 4 días?"
- "¿Es ético el uso de inteligencia artificial en la medicina?"
- "¿Deberíamos invertir en energía nuclear o renovables?"
- "¿La educación universitaria debería ser gratuita?"
- "¿Los vehículos autónomos deberían reemplazar conductores humanos?"

## 🔧 Configuración Avanzada

### Cambiar Modelos LLM

En `backend/.env`:
```env
MODEL_GEMINI=llama-3.3-70b-versatile  # Modelo complejo
MODEL_LLAMA=llama-3.1-8b-instant      # Modelo rápido
```

### Agregar Documentos al RAG

1. Coloca archivos `.txt` o `.md` en `backend/app/rag/data/{categoria}/`
2. Categorías: `estudios`, `estadisticas`, `casos_historicos`, `falacias`
3. Elimina `backend/chroma_db/` para forzar recarga
4. Reinicia el backend para indexar automáticamente

Ver [Backend README](./backend/README.md#agregar-documentos) para más detalles.

## 🐛 Troubleshooting

### Error con Python 3.13+

**Problema:** Errores de instalación o incompatibilidad con dependencias

**Solución:**
1. Desinstala Python 3.13
2. Instala Python 3.12 desde [python.org/downloads](https://www.python.org/downloads/)
3. Verifica la versión:
```bash
python --version  # Debe mostrar 3.10.x, 3.11.x o 3.12.x
```

**Razón:** ChromaDB y algunas dependencias de sentence-transformers aún no son compatibles con Python 3.13.

### Backend no inicia

**Problema:** Error con ChromaDB o dependencias

**Solución:**
```bash
pip install --upgrade chromadb sentence-transformers
```

### Frontend no conecta

**Problema:** CORS o backend no disponible

**Solución:**
1. Verifica backend en http://localhost:8000/api/v1/health
2. Revisa CORS en `backend/main.py`
3. Verifica `VITE_API_URL` en `frontend/.env`

### Rate Limiting de Groq

**Problema:** Errores 429 (Too Many Requests)

**Solución:**
1. El delay actual es 2.5s (respeta límite de 1K RPM para 70b)
2. Si persiste, aumenta en `backend/.env`:
```env
API_CALL_DELAY=3.0
```
3. O reduce rondas:
```env
DEFAULT_ROUNDS=2
```

### SSE se desconecta

**Problema:** Streaming interrumpido

**Solución:**
1. Revisa logs del backend por errores
2. Verifica estabilidad de red
3. Aumenta timeouts si necesario

## 🚀 Quick Start

```bash
# 1. Clonar
git clone <repo-url>
cd ai-parlament

# 2. Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tu Groq API key (gsk_...)
python main.py &

# 3. Frontend
cd ../frontend
npm install
npm run dev

# 4. Abrir http://localhost:5173 y listo!
```
