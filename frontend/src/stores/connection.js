import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useConnectionStore = defineStore('connection', () => {
    // --- ESTADO ---
    const isOnline = ref(navigator.onLine); // Estado inicial del navegador
    const connectionType = ref('unknown'); // 'wifi', 'cellular', 'none', 'unknown'
    const serverReachable = ref(true); // Asumimos true al inicio hasta probar lo contrario
    const isSyncing = ref(false);
    
    // Estados temporales (banderas booleanas)
    const showSuccess = ref(false);
    const showCatastrophicError = ref(false);
    
    const syncErrorMessage = ref(null);

    // Timers
    let successTimer = null;
    let errorTimer = null;

    // --- COMPUTED: Determinar estado actual (Prioridades) ---
    const connectionStatus = computed(() => {
        // 1. Error Catastrófico (Prioridad Máxima - Morado Parpadeante)
        if (showCatastrophicError.value) {
            return {
                color: '#9C27B0', // Morado
                pulse: true,
                type: 'catastrophic_error',
                text: 'Error Crítico'
            };
        }

        // 2. Sincronización Exitosa (Azul Parpadeante)
        if (showSuccess.value) {
            return {
                color: '#2196F3', // Azul
                pulse: true,
                type: 'sync_success',
                text: 'Sincronizado'
            };
        }

        // 3. Sin Internet (Naranja)
        // Se considera sin internet si navigator.onLine es false o connectionType es 'none'
        if (!isOnline.value || connectionType.value === 'none') {
            return {
                color: '#FFFFFF', // Blanco
                pulse: false,
                type: 'no_internet',
                text: 'Sin Conexión'
            };
        }

        // 4. Servidor Inaccesible (Rojo)
        // Hay internet, pero el servidor no responde
        if (!serverReachable.value) {
            return {
                color: '#F44336', // Rojo
                pulse: false,
                type: 'server_down',
                text: 'Servidor Inaccesible'
            };
        }

        // 5. Modo Ahorro / Datos Móviles (Blanco)
        if (connectionType.value === 'cellular') {
            return {
                color: '#FF9800', // Naranja
                pulse: isSyncing.value, // Opcional: parpadear levemente si está sincronizando
                type: 'cellular',
                text: 'Datos Móviles'
            };
        }

        // 6. Conectado WiFi + Servidor OK (Verde)
        // 6. Conectado WiFi + Servidor OK (Verde)
        // Eliminamos 'unknown' de aquí incondicionalmente.
        if (connectionType.value === 'wifi') {
            return {
                color: '#4CAF50', // Verde
                pulse: isSyncing.value, // Pulso sutil si está sincronizando
                type: 'wifi',
                text: 'Conectado'
            };
        }
        
        // 7. Fallback para 'unknown' pero con internet detectado (Verde o Gris)
        // A veces PC o emuladores dan 'unknown'. Si isOnline es true y el servidor responde, asumimos verde.
        if (connectionType.value === 'unknown' && isOnline.value && serverReachable.value) {
            return {
                color: '#4CAF50', // Verde (Asumimos cable/ethernet)
                pulse: isSyncing.value,
                type: 'unknown_online',
                text: 'Conectado'
            };
        }

        // 8. Fallback general (Gris) - Estado indeterminado real
        return {
            color: '#757575',
            pulse: false,
            type: 'unknown',
            text: 'Desconocido'
        };

        // 7. Fallback (Gris)
        return {
            color: '#757575',
            pulse: false,
            type: 'unknown',
            text: 'Desconocido'
        };
    });

    // --- ACCIONES ---

    function setOnlineStatus(status) {
        isOnline.value = status;
    }

    function setConnectionType(type) {
        connectionType.value = type;
    }

    function setServerReachable(status) {
        serverReachable.value = status;
    }

    function startSync() {
        isSyncing.value = true;
        // Limpiamos estados temporales previos al iniciar
        showSuccess.value = false;
        showCatastrophicError.value = false;
    }

    function syncSuccess() {
        isSyncing.value = false;
        serverReachable.value = true;
        
        // Mostrar estado de éxito
        showSuccess.value = true;
        
        // Resetear timer anterior si existe
        if (successTimer) clearTimeout(successTimer);
        
        // Ocultar después de 3 segundos
        successTimer = setTimeout(() => {
            showSuccess.value = false;
            successTimer = null;
        }, 3000);
    }

    function syncError(message, isCatastrophic = false) {
        isSyncing.value = false;
        syncErrorMessage.value = message;
        
        if (isCatastrophic) {
            showCatastrophicError.value = true;
            
            if (errorTimer) clearTimeout(errorTimer);
            
            errorTimer = setTimeout(() => {
                showCatastrophicError.value = false;
                errorTimer = null;
            }, 5000);
        }
    }

    function reset() {
        showSuccess.value = false;
        showCatastrophicError.value = false;
        isSyncing.value = false;
        if (successTimer) clearTimeout(successTimer);
        if (errorTimer) clearTimeout(errorTimer);
    }

    return {
        // State
        isOnline,
        connectionType,
        serverReachable,
        isSyncing,
        syncErrorMessage,
        
        // Computed
        connectionStatus,

        // Actions
        setOnlineStatus,
        setConnectionType,
        setServerReachable,
        startSync,
        syncSuccess,
        syncError,
        reset
    };
});
