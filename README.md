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
- 💰 **Modelos Gratuitos** (Google Gemini Flash 1.5 + Meta Llama 3.1 8B)

## 🎬 Demo Rápido

```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tu OPENROUTER_API_KEY
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
- **OpenRouter** para acceso a LLMs (Gemini + Llama)
- **Sentence-Transformers** para embeddings
- **Server-Sent Events** para streaming

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
│   │   ├── llm/      # Cliente OpenRouter
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

3. **Debate Libre** (5 rondas)
   - Agentes responden y contraargumentan
   - Moderador identifica puntos de tensión
   - Crítico señala falacias

4. **Interpelaciones**
   - Moderador genera preguntas clave
   - Respuestas dirigidas y obligatorias

5. **Síntesis**
   - Sintetizador analiza todo el debate
   - Identifica consensos y disensos
   - Propone soluciones híbridas

6. **Resultado**
   - Acta completa descargable
   - Resumen ejecutivo
   - Conclusiones balanceadas

## 🚀 Instalación Completa

### Requisitos Previos

- Python 3.10+
- Node.js 18+
- OpenRouter API Key (gratuita en https://openrouter.ai/)

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
# Editar .env y añadir: OPENROUTER_API_KEY=tu_key_aqui

# Iniciar servidor
python main.py
```

Backend disponible en: **http://localhost:8000**
Documentación API: **http://localhost:8000/docs**

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

En `backend/app/core/config.py`:
```python
AGENT_MODELS = {
    AgentRole.MODERADOR: "google/gemini-flash-1.5",
    AgentRole.ECONOMISTA: "meta-llama/llama-3.1-8b-instruct",
    # ... personalizar aquí
}
```

### Agregar Documentos al RAG

1. Coloca archivos `.txt` o `.md` en `backend/app/rag/data/{categoria}/`
2. Categorías: estudios, estadisticas, casos_historicos, falacias
3. Reinicia el servidor para indexar

### Personalizar Colores de Agentes

En `frontend/src/App.tsx`:
```typescript
const AGENTES_INFO: Record<string, AgenteInfo> = {
  economista: {
    color: 'bg-green-500',  // Cambiar aquí
    // ...
  }
}
```

## 🐛 Troubleshooting

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

### Rate Limiting de OpenRouter

**Problema:** Muchos requests 429

**Solución:**
Aumenta `API_CALL_DELAY` en `backend/.env`:
```env
API_CALL_DELAY=1.0
```

### SSE se desconecta

**Problema:** Streaming interrumpido

**Solución:**
1. Revisa logs del backend por errores
2. Verifica estabilidad de red
3. Aumenta timeouts si necesario

## 📊 Estadísticas del Proyecto

- **Backend**: 43 archivos, ~5,200 líneas de código
- **Frontend**: 20 archivos, ~1,500 líneas de código
- **Total**: 63 archivos, ~6,700 líneas de código
- **Agentes**: 11 especializados
- **Documentos RAG**: 7 ejemplos en 4 categorías
- **API Endpoints**: 8 principales
- **Tests**: 9 tests básicos

## 🤝 Contribuir

1. Fork el repositorio
2. Crea tu rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 🔐 Consideraciones Éticas

Este sistema es una **herramienta de exploración** que:
- ✅ Ayuda a analizar temas desde múltiples perspectivas
- ✅ Genera insights valiosos para toma de decisiones
- ❌ NO reemplaza análisis humano crítico
- ❌ NO es apto para decisiones legales, médicas o financieras certificadas
- ⚠️ Puede tener sesgos inherentes de los LLMs subyacentes

**Disclaimer:** Las conclusiones generadas deben ser evaluadas críticamente por humanos antes de tomar decisiones importantes.

## 📄 Licencia

[Especificar licencia]

## 🙏 Agradecimientos

- **OpenRouter** - Acceso a LLMs gratuitos
- **Anthropic Claude** - Asistencia en desarrollo
- **shadcn/ui** - Componentes UI de calidad
- **FastAPI** - Framework backend eficiente
- **Vite** - Build tool ultra-rápido

## 📧 Contacto

[Información de contacto]

---

**Versión**: 1.0.0
**Última actualización**: 2024-11-06

Construido con ❤️ usando Python, React, y IA de vanguardia

---

## 🚀 Quick Start

```bash
# 1. Clonar
git clone <repo-url>
cd ai-parlament

# 2. Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
# Editar .env con OPENROUTER_API_KEY
python main.py &

# 3. Frontend
cd ../frontend
npm install
npm run dev

# 4. Abrir http://localhost:5173 y disfrutar! 🎉
```
