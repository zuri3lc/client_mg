import { Network } from '@capacitor/network';
import { App } from '@capacitor/app';
import { syncData } from './sync'; // Tu función de sync existente
import api from './api'; // Tu instancia de Axios
import { useAuthStore } from '@/stores/auth';
import { useUIStore } from '@/stores/ui'; // Importar store de UI
import { LocalNotifications } from '@capacitor/local-notifications';
import { db } from './db';

const REMINDER_ID = 1001; // ID fijo para nuestra notificación de recordatorio



// Configuración de tiempos (en milisegundos)
const INTERVALO_WIFI = 5 * 60 * 1000;      // 5 minutos
const INTERVALO_DATOS = 30 * 60 * 1000;    // 30 minutos

let intervaloActivo = null; // Para guardar el ID del timer y poder cancelarlo
let isSyncing = false;      // Semáforo para no solapar sincronizaciones

// Helper para notificar sin romper si el store no está listo
function notify(msg, type = 'info') {
    try {
        const ui = useUIStore();
        ui.showSnackbar(msg, type);
    } catch (e) {
        // Si Pinia no está listo, solo logueamos
        console.log('[Notify Skipped]', msg);
    }
}


/**
 * 1. El Explorador: Verifica si el servidor responde
 */
async function checkServerStatus() {
    try {
        // Hacemos una petición ligera a la raíz o un endpoint de salud
        // Ajusta '/health' o '/' según tu backend FastAPI
        await api.pingServer(); 
        return true;
    } catch (error) {
        console.warn('Servidor no accesible:', error.message);
        return false;
    }
}

/**
 * 2. La Acción: Ejecuta la sincronización si todo está bien
 */
async function tryToSync() {
    if (isSyncing) return; 

    let authStore;
    try {
        authStore = useAuthStore();
    } catch (e) {
        return; // El store no está listo, abortamos silenciosamente
    }

    if (!authStore.accessToken) {
        return; 
    }
    
    // Primero, verificamos conexión física
    const status = await Network.getStatus();

    if (!status.connected) {
        console.log('No hay internet, saltando sync.');
        notify('Sin conexión a Internet: Sincronización pausada', 'warning');
        return;
    }


    // Segundo, verificamos si el servidor "realmente" está ahí
    const serverAlive = await checkServerStatus();
    
    if (!serverAlive) return;

    try {
        isSyncing = true;
        console.log('--- AutoSync Iniciado ---');
        // notify('Sincronizando datos...', 'info'); // Opcional: reducir ruido visual si es muy frecuente
        
        await syncData(); // Tu magia de sincronización
        
        console.log('--- AutoSync Finalizado ---');
        notify('Sincronización completada exitosamente', 'success');
    } catch (error) {
        console.error('Error en AutoSync:', error);
        notify('Error al sincronizar datos', 'error');
    } finally {
        isSyncing = false;
    }
}

/**
 * 3. El Gestor: Decide qué ritmo usar
 */
function programarIntervalo(tipoConexion) {
    // Limpiamos cualquier intervalo anterior
    if (intervaloActivo) clearInterval(intervaloActivo);

    let tiempo;
    
    if (tipoConexion === 'wifi') {
        tiempo = INTERVALO_WIFI;
        console.log(`Modo WiFi detectado: Sync cada ${INTERVALO_WIFI/1000/60} min`);
        notify('Conexión WiFi detectada: Sincronización rápida activa', 'success');
        // En WiFi, intentamos sincronizar inmediatamente al conectarnos
        tryToSync(); 
    } else if (tipoConexion === 'cellular') {
        tiempo = INTERVALO_DATOS;
        console.log(`Modo Datos detectado: Sync cada ${INTERVALO_DATOS/1000/60} min`);
        notify('Datos móviles detectados: Sincronización en modo ahorro', 'info');
    } else {
        console.log('Conexión desconocida o nula. Pausando auto-sync.');
        notify('Sin conexión estable: Sincronización pausada', 'warning');
        return; // No programamos nada si no hay red
    }

    // Iniciamos el ciclo
    intervaloActivo = setInterval(tryToSync, tiempo);
}

/**
 * 4. El Guardián: Programa recordatorios si hay cosas pendientes
 */
async function scheduleSyncReminder() {
    try {
        // 1. Verificamos si hay algo que valga la pena sincronizar
        const pendingClients = await db.clients.where('needsSync').above(0).count();
        const pendingMovements = await db.movimientos.where('needsSync').above(0).count();
        const totalPending = pendingClients + pendingMovements;

        if (totalPending > 0) {
            console.log(`💤 App en pausa con ${totalPending} cambios pendientes. Programando recordatorio...`);
            
            // Programamos notificación para dentro de 1 hora (60 min * 60 seg * 1000 ms)
             // Para pruebas rápidas podrías usar 30000 (30 seg), pero dejamos 1 hora como pediste
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
    // A. Configuración Inicial de Notificaciones
    try {
        // Solicitar permisos (necesario en Android 13+ e iOS)
        const permStatus = await LocalNotifications.requestPermissions();
        if (permStatus.display === 'granted') {
             // Crear canal (solo afecta Android)
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
        programarIntervalo(status.connectionType);
    });

    // D. Listener para acciones de notificación (Si tocan la alerta)
    LocalNotifications.addListener('localNotificationActionPerformed', (notification) => {
        if (notification.notification.id === REMINDER_ID) {
            console.log('🔔 Usuario tocó el recordatorio. Iniciando sincronización...');
            // Al abrirse la app por la notificación, intentamos sincronizar
            // Nota: La lógica de 'isActive' también correrá, así que es un doble seguro.
            tryToSync();
        }
    });

    // B. Escuchar cambios de estado (Segundo Plano / Primer Plano)
    App.addListener('appStateChange', async ({ isActive }) => {
        if (isActive) {
            // -- AL VOLVER --
            console.log('📱 App activa nuevamente: Comprobando sincronización...');
            
            // Cancelamos cualquier recordatorio pendiente porque ya volvió el usuario
            await LocalNotifications.cancel({ notifications: [{ id: REMINDER_ID }] });
            
            notify('Aplicación activa: Verificando cambios...', 'info');
            tryToSync();
        } else {
            // -- AL DORMIR (PAUSA) --
            // Verificamos si dejamos cosas pendientes
            scheduleSyncReminder();
        }
    });

    // C. Obtener estado inicial y arrancar
    const status = await Network.getStatus();
    programarIntervalo(status.connectionType);
}