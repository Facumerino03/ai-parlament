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

### Personalizar Colores de Agentes

Edita en `App.tsx` el objeto `AGENTES_INFO`:
```typescript
economista: {
  nombre: 'Economista',
  rol: 'Análisis Económico',
  color: 'bg-green-500',  // Cambiar aquí
  icon: 'TrendingUp'
}
```

## 🐛 Troubleshooting

### "Error de conexión CORS"

**Problema**: El backend no permite requests desde localhost:5173

**Solución**: Verifica que el backend tenga CORS configurado correctamente en `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    ...
)
```

### "Backend no disponible"

**Problema**: No puede conectar al backend

**Solución**:
1. Verifica que el backend esté corriendo: `curl http://localhost:8000/api/v1/health`
2. Verifica `VITE_API_URL` en `.env`
3. Revisa logs del backend para errores

### "SSE se desconecta constantemente"

**Problema**: La conexión de streaming se pierde

**Solución**:
1. El backend puede estar tomando mucho tiempo (rate limits)
2. Verifica logs del backend por errores de OpenRouter
3. Aumenta `API_CALL_DELAY` en el backend si hay rate limiting

### "Los argumentos no aparecen"

**Problema**: El debate inicia pero no se ven argumentos

**Solución**:
1. Abre la consola del navegador (F12) y busca errores
2. Verifica la pestaña "Network" para ver si llegan eventos SSE
3. Verifica que el backend esté generando argumentos (logs)

## 📱 Responsive Design

La aplicación está optimizada para:

- **Desktop** (>1024px): Grid completo de agentes, layout espacioso
- **Tablet** (640-1024px): Grid adaptado, scroll en stream
- **Mobile** (<640px): Grid compacto 2 columnas, layout vertical

## 🎨 Personalización de Estilos

### Cambiar Tema de Colores

Edita `src/index.css`:
```css
:root {
  --primary: 221.2 83.2% 53.3%;  /* Tu color primario */
  --secondary: 210 40% 96.1%;    /* Color secundario */
  ...
}
```

### Añadir Animaciones Personalizadas

En `tailwind.config.js`:
```javascript
extend: {
  keyframes: {
    'tu-animacion': {
      '0%': { ... },
      '100%': { ... },
    }
  },
  animation: {
    'tu-animacion': 'tu-animacion 1s ease-in-out',
  }
}
```

## 🚀 Despliegue

### Vercel / Netlify

1. Build del proyecto:
   ```bash
   npm run build
   ```

2. Sube la carpeta `dist/` a tu servicio de hosting

3. Configura variables de entorno:
   - `VITE_API_URL`: URL de tu backend en producción

### Docker

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## 📄 Licencia

[Especificar licencia]

## 📧 Soporte

Si encuentras problemas:
1. Revisa la sección de Troubleshooting
2. Verifica que el backend esté corriendo correctamente
3. Consulta los logs del navegador (F12 → Console)
4. Abre un issue en GitHub con detalles del error

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

**Versión**: 1.0.0
**Última actualización**: 2024-11-06
**Desarrollado con** ❤️ **y React**
