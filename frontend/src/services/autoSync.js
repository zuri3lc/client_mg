import { Network } from '@capacitor/network';
import { App } from '@capacitor/app';
import { syncData } from './sync'; 
import api from './api'; 
import { useAuthStore } from '@/stores/auth';
import { useConnectionStore } from '@/stores/connection';
import { LocalNotifications } from '@capacitor/local-notifications';
import { db } from './db';

const REMINDER_ID = 1001; 

const INTERVALO_WIFI = 5 * 60 * 1000;      
const INTERVALO_DATOS = 30 * 60 * 1000;    
const INTERVALO_HEARTBEAT = 20 * 1000; // 20 segundos para detección rápida

let intervaloActivo = null; 
let heartbeatId = null; // ID para el intervalo del latido
let isSyncing = false;      

// Helper para acceder al store de forma segura
function getConnectionStore() {
    try {
        return useConnectionStore();
    } catch (e) {
        return null;
    }
}

/**
 * 1. El Explorador: Verifica si el servidor responde
 * Ahora actualiza proactivamente el store
 */
async function checkServerStatus() {
    const connStore = getConnectionStore();
    // Si no hay red física, ni intentamos ping (ahorramos batería y errores feos)
    const netStatus = await Network.getStatus();
    if (!netStatus.connected) {
        if (connStore) connStore.setOnlineStatus(false);
        return false;
    }

    try {
        await api.pingServer(); 
        if (connStore) {
            connStore.setServerReachable(true);
            connStore.setOnlineStatus(true); // Reconfirmamos que hay linea
        }
        return true;
    } catch (error) {
        console.warn('💔 Heartbeat: Servidor no responde'); // Comentar para menos ruido si se desea
        if (connStore) connStore.setServerReachable(false);
        return false;
    }
}

/**
 * NUEVO: El Cardiólogo - Mantiene el pulso de la conexión constante
 * Ejecuta un ping ligero independiente de la sincronización de datos
 */
function startHeartbeat() {
    if (heartbeatId) clearInterval(heartbeatId);

    console.log(`💓 Iniciando Heartbeat de conexión (cada ${INTERVALO_HEARTBEAT/1000}s)`);
    
    // Ejecutar uno inmediato al arrancar
    checkServerStatus();

    heartbeatId = setInterval(async () => {
        // Solo "latimos" si no estamos en medio de una sync pesada para no saturar
        if (!isSyncing) {
            await checkServerStatus();
        }
    }, INTERVALO_HEARTBEAT);
}

/**
 * 2. La Acción: Ejecuta la sincronización si todo está bien
 */
async function tryToSync() {
    if (isSyncing) return; 

    isSyncing = true; // 🔒 Bloqueamos inmediatamente para evitar condiciones de carrera

    try {
        const connStore = getConnectionStore();
        let authStore;
        try {
            authStore = useAuthStore();
        } catch (e) {
            return; 
        }

        if (!authStore.accessToken) {
            return; 
        }
        
        // Primero, verificamos conexión física
        const status = await Network.getStatus();

        if (!status.connected) {
            console.log('No hay internet, saltando sync.');
            // El store se actualiza vía listener, pero forzamos por si acaso
            if (connStore) connStore.setOnlineStatus(false);
            return;
        }

        // Segundo, verificamos si el servidor "realmente" está ahí
        const serverAlive = await checkServerStatus();
        
        if (!serverAlive) return;

        // Si llegamos aquí, vamos a sincronizar
        if (connStore) connStore.startSync();
        
        console.log('--- AutoSync Iniciado ---');
        
        await syncData(); 
        
        console.log('--- AutoSync Finalizado ---');
        if (connStore) connStore.syncSuccess();
    } catch (error) {
        console.error('Error en AutoSync:', error);
        
        // Determinar gravedad
        const connStore = getConnectionStore();
        const isCatastrophic = error.response?.status >= 500 || error.code === 'ERR_NETWORK';
        if (connStore) connStore.syncError(error.message, isCatastrophic);
    } finally {
        isSyncing = false; // 🔓 Liberamos el lock siempre, pase lo que pase
    }
}

/**
 * 3. El Gestor: Decide qué ritmo usar
 */
function programarIntervalo(tipoConexion) {
    if (intervaloActivo) clearInterval(intervaloActivo);

    let tiempo;
    
    // Actualizamos el store con el tipo de conexión
    const connStore = getConnectionStore();
    console.log(`[AutoSync] Detectando tipo de conexión: '${tipoConexion}'`); // LOG DE DEPURACIÓN

    if (connStore) {
        connStore.setConnectionType(tipoConexion);
    }

    if (tipoConexion === 'wifi') {
        tiempo = INTERVALO_WIFI;
        console.log(`Modo WiFi detectado (Intervalo Sync: ${INTERVALO_WIFI/1000/60} min)`);
        tryToSync(); 
    } else if (tipoConexion === 'cellular') {
        tiempo = INTERVALO_DATOS;
        console.log(`Modo Datos detectado (Intervalo Sync: ${INTERVALO_DATOS/1000/60} min)`);
        // En modo datos, según la lógica, NO sincroniza automáticamente al inicio, solo programa el timer.
        // ¿Quizás quieras que sincronice una vez al conectar?
        tryToSync(); 
    } else {
        console.log('Conexión desconocida o nula. Pausando auto-sync.');
        return; 
    }

    intervaloActivo = setInterval(tryToSync, tiempo);
}

/**
 * 4. El Guardián: Programa recordatorios si hay cosas pendientes
 */
async function scheduleSyncReminder() {
    try {
        const pendingClients = await db.clients.where('needsSync').above(0).count();
        const pendingMovements = await db.movimientos.where('needsSync').above(0).count();
        const totalPending = pendingClients + pendingMovements;

        if (totalPending > 0) {
            console.log(`💤 App en pausa con ${totalPending} cambios pendientes. Programando recordatorio...`);
            
            const triggerTime = new Date(Date.now() + 60 * 60 * 1000); 

            await LocalNotifications.schedule({
                notifications: [
                    {
                        title: 'Sincronización Pendiente',
                        body: `Tienes ${totalPending} cambios sin guardar. Toca para sincronizar.`,
                        id: REMINDER_ID,
                        schedule: { at: triggerTime },
                        sound: 'default',
                        attachments: [],
                        actionTypeId: '',
                        extra: null
                    }
                ]
            });
        }
    } catch (e) {
        console.error('Error programando recordatorio:', e);
    }
}

/**
 * 5. El Inicializador: Arranca todo el sistema
 */
export async function startAutoSyncService() {
    // Inicializar estado del store
    const connStore = getConnectionStore();
    
    // A. Configuración Inicial de Notificaciones
    try {
        const permStatus = await LocalNotifications.requestPermissions();
        if (permStatus.display === 'granted') {
            await LocalNotifications.createChannel({
                id: 'sync_reminder',
                name: 'Recordatorios de Sincronización',
                importance: 3,
                visibility: 1
            });
        }
    } catch (e) {
        console.warn('No se pudieron configurar las notificaciones:', e);
    }

    // A. Escuchar cambios en la red
    Network.addListener('networkStatusChange', status => {
        console.log('Red cambió a:', status.connectionType);
        if (connStore) {
            connStore.setOnlineStatus(status.connected);
            connStore.setConnectionType(status.connectionType);
        }
        // Reprogramamos el sync de datos, pero el Heartbeat sigue su propio ritmo
        programarIntervalo(status.connectionType);
    });

    // D. Listener para acciones de notificación
    LocalNotifications.addListener('localNotificationActionPerformed', (notification) => {
        if (notification.notification.id === REMINDER_ID) {
            console.log('🔔 Usuario tocó el recordatorio. Iniciando sincronización...');
            tryToSync();
        }
    });

    // B. Escuchar cambios de estado (Segundo Plano / Primer Plano)
    App.addListener('appStateChange', async ({ isActive }) => {
        if (isActive) {
            console.log('📱 App activa nuevamente: Comprobando sincronización...');
            await LocalNotifications.cancel({ notifications: [{ id: REMINDER_ID }] });
            
            // Al volver, forzamos un chequeo inmediato
            checkServerStatus(); 
            tryToSync();
        } else {
            scheduleSyncReminder();
        }
    });

    // C. Obtener estado inicial y arrancar
    const status = await Network.getStatus();
    if (connStore) {
        connStore.setOnlineStatus(status.connected);
        connStore.setConnectionType(status.connectionType);
    }
    
    // Arrancamos los motores
    programarIntervalo(status.connectionType); // Motor datos
    startHeartbeat(); // Motor estado (Nuevo)
}