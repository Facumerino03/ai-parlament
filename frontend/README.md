# AI Parliament Frontend

Frontend moderno para el Parlamento Virtual de Debates - Una aplicación React con TypeScript que visualiza debates multidisciplinarios en tiempo real entre agentes de IA especializados.

## 🎨 Características

- **Interfaz Moderna**: Diseño limpio y profesional con Tailwind CSS y shadcn/ui
- **Tiempo Real**: Visualización de debates en vivo con Server-Sent Events (SSE)
- **Responsive**: Diseño adaptable a móvil, tablet y desktop
- **Animaciones Sutiles**: Transiciones fluidas y feedback visual
- **11 Agentes Visualizados**: Cada uno con su color e icono distintivo
- **Descarga de Actas**: Exportación de resultados en formato texto

## 🚀 Stack Tecnológico

- **React 18** + **TypeScript**
- **Vite** - Build tool ultra-rápido
- **Tailwind CSS** - Utility-first CSS
- **shadcn/ui** - Componentes accesibles y customizables
- **Lucide React** - Iconos modernos
- **Axios** - Cliente HTTP
- **EventSource API** - Streaming en tiempo real

## 📦 Requisitos

- **Node.js** 18+ y npm
- **Backend** corriendo en http://localhost:8000

## 🛠️ Instalación

### 1. Instalar Dependencias

```bash
cd frontend
npm install
```

### 2. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env si el backend está en otra URL
# Por defecto: VITE_API_URL=http://localhost:8000
```

### 3. Verificar que el Backend Esté Corriendo

```bash
# En otra terminal, desde backend/
python main.py

# Verificar que responda:
curl http://localhost:8000/api/v1/health
```

## ▶️ Desarrollo

```bash
npm run dev
```

La aplicación estará disponible en: **http://localhost:5173**

## 🏗️ Build para Producción

```bash
npm run build
```

Los archivos compilados estarán en `dist/`

Para preview del build:
```bash
npm run preview
```

## 📂 Estructura del Proyecto

```
frontend/
├── public/
│   └── vite.svg                 # Favicon
├── src/
│   ├── components/
│   │   └── ui/                  # Componentes shadcn/ui base
│   │       ├── button.tsx
│   │       └── card.tsx
│   ├── services/
│   │   └── api.ts               # Cliente API
│   ├── types/
│   │   └── debate.ts            # TypeScript interfaces
│   ├── lib/
│   │   └── utils.ts             # Utilidades (cn helper, formatters)
│   ├── App.tsx                  # Componente principal
│   ├── main.tsx                 # Entry point
│   └── index.css                # Estilos globales + Tailwind
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── README.md
```

## 🎯 Funcionalidades Principales

### 1. Iniciar un Debate

1. Ingresa un tema en el textarea (máx. 500 caracteres)
2. Click en "Iniciar Debate"
3. El sistema se conecta al backend y comienza el debate

### 2. Visualización en Tiempo Real

- **Grid de Agentes**: Muestra los 11 agentes con sus colores e iconos
- **Resaltado Dinámico**: El agente que está hablando se ilumina con animación
- **Stream de Argumentos**: Los argumentos aparecen conforme se generan
- **Barra de Progreso**: Indica fase actual y progreso

### 3. Resultado Final

Al completar el debate:
- Resumen ejecutivo
- Consensos alcanzados
- Disensos remanentes
- Propuestas híbridas
- Botón para descargar acta completa

### 4. Manejo de Errores

- Mensajes claros en caso de fallos
- Reconexión automática en caso de pérdida de conexión SSE
- Validación de inputs

## 🎨 Componentes Principales

### `App.tsx`
Componente principal que orquesta:
- Formulario de inicio
- Conexión SSE
- Grid de agentes
- Stream de argumentos
- Resultado final

### `services/api.ts`
Cliente API con métodos:
- `iniciarDebate(request)` - Crea nuevo debate
- `ejecutarDebate(id)` - Trigger ejecución
- `obtenerEstado(id)` - Estado actual
- `obtenerResultado(id)` - Resultado completo
- `getStreamUrl(id)` - URL para SSE

### `types/debate.ts`
Interfaces TypeScript para:
- Requests y responses
- Tipos de argumentos
- Configuración de agentes
- Eventos SSE

## 🔧 Configuración Avanzada

### Cambiar URL del Backend

Edita `.env`:
```env
VITE_API_URL=http://tu-servidor:8000
```

### Cambiar Puerto del Frontend

Edita `vite.config.ts`:
```typescript
server: {
  port: 3000, // Cambiar aquí
  ...
}
```

## 🎉 Demo

Para probar rápidamente:

```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
cd frontend
npm install
npm run dev

# Abre http://localhost:5173
```

**Ejemplo de tema para probar:**
- "¿Debería implementarse una semana laboral de 4 días?"
- "¿Es ético el uso de inteligencia artificial en la medicina?"
- "¿Deberíamos invertir en energía nuclear o renovables?"

---
