# Sistema de Notificaciones de Conexión

## 📊 Descripción General

Sistema visual de notificaciones basado en una **barra de estado de 10px** que muestra el estado de conexión y sincronización de forma elegante y no intrusiva.

## 🎨 Estados y Colores

### Estados Principales

| Color                      | Estado               | Descripción                                |
| -------------------------- | -------------------- | ------------------------------------------ |
| 🟢 **Verde** (`#4CAF50`)   | Conectado (WiFi)     | Conexión WiFi activa + Servidor alcanzable |
| 🟠 **Naranja** (`#FF9800`) | Modo Ahorro          | Datos móviles + Servidor alcanzable        |
| ⚪ **Blanco** (`#FFFFFF`)  | Sin Internet         | No hay conexión a Internet                 |
| 🔴 **Rojo** (`#F44336`)    | Servidor Inaccesible | Hay Internet pero el servidor no responde  |
| ⚫ **Gris** (`#757575`)    | Desconocido          | Estado inicial o indeterminado             |

### Estados Temporales (Parpadeantes)

| Color                     | Estado                 | Duración   | Descripción                                            |
| ------------------------- | ---------------------- | ---------- | ------------------------------------------------------ |
| 🔵 **Azul** (`#2196F3`)   | Sincronización Exitosa | 3 segundos | Aparece después de una sincronización exitosa          |
| 🟣 **Morado** (`#9C27B0`) | Error Catastrófico     | 5 segundos | Error crítico en la sincronización (500+, ERR_NETWORK) |

## 🏗️ Arquitectura

### Componentes

1. **`connectionStore.js`** - Store de Pinia que gestiona el estado
2. **`ConnectionStatusBar.vue`** - Componente visual de la barra
3. **`autoSync.js`** - Servicio de sincronización automática (actualizado)
4. **`sync.js`** - Servicio de sincronización manual (actualizado)
5. **`AppLayout.vue`** - Layout principal (integra la barra)

### Flujo de Datos

```
Network/Server Events
        ↓
autoSync.js / sync.js
        ↓
connectionStore (Pinia)
        ↓
ConnectionStatusBar.vue
        ↓
Visual Feedback (Barra de color)
```

## 🔧 API del Store

### Estado

```javascript
const connectionStore = useConnectionStore()

// Propiedades reactivas
connectionStore.isOnline // Boolean: ¿Hay internet?
connectionStore.connectionType // String: 'wifi' | 'cellular' | 'none' | 'unknown'
connectionStore.serverReachable // Boolean: ¿El servidor responde?
connectionStore.isSyncing // Boolean: ¿Sincronización en progreso?
connectionStore.lastSyncSuccess // Number: Timestamp del último éxito
connectionStore.lastSyncError // Number: Timestamp del último error
connectionStore.syncErrorMessage // String: Mensaje del error

// Computed
connectionStore.connectionStatus // Object: { color, text, type, pulse }
```

### Acciones

```javascript
// Actualizar estado de internet
connectionStore.setOnlineStatus(true / false)

// Actualizar tipo de conexión
connectionStore.setConnectionType('wifi' | 'cellular' | 'none' | 'unknown')

// Actualizar alcance del servidor
connectionStore.setServerReachable(true / false)

// Marcar inicio de sincronización
connectionStore.startSync()

// Marcar sincronización exitosa (muestra flash azul)
connectionStore.syncSuccess()

// Marcar error de sincronización
connectionStore.syncError(message, isCatastrophic)

// Resetear todo
connectionStore.reset()
```

## 💡 Uso en Servicios

### En autoSync.js o sync.js

```javascript
import { useConnectionStore } from '@/stores/connection'

async function mySync() {
  let connectionStore
  try {
    connectionStore = useConnectionStore()
  } catch (e) {
    // Store no disponible aún
  }

  try {
    // Marcar inicio
    if (connectionStore) {
      connectionStore.startSync()
    }

    // ... tu lógica de sincronización ...

    // Marcar éxito
    if (connectionStore) {
      connectionStore.syncSuccess()
    }
  } catch (error) {
    // Determinar gravedad
    const isCatastrophic = error.response?.status >= 500 || error.code === 'ERR_NETWORK'

    // Reportar error
    if (connectionStore) {
      connectionStore.syncError(error.message, isCatastrophic)
    }
  }
}
```

## 🎯 Prioridades de Estados

El sistema usa un sistema de prioridades para determinar qué mostrar:

1. **Error Catastrófico** (Morado parpadeante)
2. **Sincronización Exitosa** (Azul parpadeante)
3. **Sin Internet** (Naranja)
4. **Servidor Inaccesible** (Rojo)
5. **Datos Móviles** (Blanco)
6. **WiFi Conectado** (Verde)
7. **Desconocido** (Gris)

## 🎨 Animaciones

### Pulso (para estados temporales)

```css
@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}
```

### Shimmer (efecto de brillo sutil)

```css
@keyframes shimmer {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
}
```

## 📱 Integración en la UI

La barra se coloca justo **debajo del `v-app-bar`** en `AppLayout.vue`:

```vue
<v-app-bar>
    <!-- ... contenido del app bar ... -->
</v-app-bar>

<!-- Barra de estado de conexión -->
<ConnectionStatusBar />

<v-main>
    <!-- ... contenido principal ... -->
</v-main>
```

## 🔄 Sincronización con Network API

El sistema se integra automáticamente con:

- **Navigator.onLine** - Estado de internet del navegador
- **Capacitor Network Plugin** - Tipo de conexión (WiFi/Cellular)
- **API Ping** - Verificación de alcance del servidor

## ⚡ Ventajas

1. **No Intrusivo** - Solo 10px de altura, no interrumpe el flujo
2. **Siempre Visible** - Información constante del estado
3. **Feedback Inmediato** - Cambios de estado se reflejan al instante
4. **Reduce Snackbars** - Menos notificaciones emergentes molestas
5. **Elegante** - Animaciones sutiles y colores bien definidos

## 🚀 Mejoras Futuras

- [ ] Agregar tooltip con información detallada al hacer hover
- [ ] Sonidos sutiles para cambios de estado (opcional)
- [ ] Historial de eventos de sincronización
- [ ] Modo debug con información técnica
- [ ] Personalización de colores por tema

## 📝 Notas

- Los estados temporales (azul/morado) tienen **prioridad máxima**
- El sistema es **tolerante a fallos** - si el store no está disponible, no rompe
- Los **snackbars se reducen** - solo para errores catastróficos
- La barra es **completamente visual** - sin texto, solo colores
