import { Network } from '@capacitor/network';
import { App } from '@capacitor/app';
import { syncData } from './sync'; // Tu función de sync existente
import api from './api'; // Tu instancia de Axios
import { useAuthStore } from '@/stores/auth';

// Configuración de tiempos (en milisegundos)
const INTERVALO_WIFI = 5 * 60 * 1000;      // 5 minutos
const INTERVALO_DATOS = 30 * 60 * 1000;    // 30 minutos

let intervaloActivo = null; // Para guardar el ID del timer y poder cancelarlo
let isSyncing = false;      // Semáforo para no solapar sincronizaciones

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
        return;
    }

    // Segundo, verificamos si el servidor "realmente" está ahí
    const serverAlive = await checkServerStatus();
    
    if (!serverAlive) return;

    try {
        isSyncing = true;
        console.log('--- AutoSync Iniciado ---');
        await syncData(); // Tu magia de sincronización
        console.log('--- AutoSync Finalizado ---');
    } catch (error) {
        console.error('Error en AutoSync:', error);
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
        // En WiFi, intentamos sincronizar inmediatamente al conectarnos
        tryToSync(); 
    } else if (tipoConexion === 'cellular') {
        tiempo = INTERVALO_DATOS;
        console.log(`Modo Datos detectado: Sync cada ${INTERVALO_DATOS/1000/60} min`);
    } else {
        console.log('Conexión desconocida o nula. Pausando auto-sync.');
        return; // No programamos nada si no hay red
    }

    // Iniciamos el ciclo
    intervaloActivo = setInterval(tryToSync, tiempo);
}

/**
 * 4. El Inicializador: Arranca todo el sistema
 */
export async function startAutoSyncService() {
    // A. Escuchar cambios en la red
    Network.addListener('networkStatusChange', status => {
        console.log('Red cambió a:', status.connectionType);
        programarIntervalo(status.connectionType);
    });

    // B. Escuchar cuando la app vuelve a primer plano (Resume)
    App.addListener('appStateChange', ({ isActive }) => {
        if (isActive) {
            console.log('📱 App activa nuevamente: Comprobando sincronización...');
            tryToSync();
        }
    });

    // C. Obtener estado inicial y arrancar
    const status = await Network.getStatus();
    programarIntervalo(status.connectionType);
}