// src/services/sync.js
import { db } from './db';
import api from './api';

let isSyncing = false;
let syncIntervalId = null;

// La función principal que se encargará de subir los datos
export const syncData = async () => {
    if (isSyncing || !navigator.onLine) {
        if (!navigator.onLine) console.log('Offline, se omite el intento de sincronización.');
        return;
    }

    try {
        // Antes de hacer el trabajo pesado, intentamos llegar al servidor.
        await api.pingServer();
        console.log('✅ Conexión con el servidor confirmada.');
    } catch (error) {
        // Si el ping falla, significa que no hay una conexión real a internet.
        console.log('⚠️ No se pudo conectar con el servidor. Se aborta la sincronización.');
        return; // Detenemos la ejecución.
    }

    isSyncing = true;
    console.log('🚀 Iniciando proceso de sincronización: Local -> Remoto');

    try {
        // --- 1. SINCRONIZACIÓN DE CLIENTES NUEVOS (needsSync: 1) ---
        const clientsToCreate = await db.clients.where('needsSync').equals(1).toArray();
        if (clientsToCreate.length > 0) {
            console.log(`Enviando ${clientsToCreate.length} clientes nuevos...`);
            for (const localClient of clientsToCreate) {
                try {
                    const payload = {
                        nombre: localClient.nombre,
                        telefono: localClient.telefono,
                        ubicacion_aproximada: localClient.ubicacion_aproximada,
                        comentario: localClient.comentario,
                        saldo_inicial: localClient.saldo_actual
                    };
                    const response = await api.createClient(payload);
                    const serverClient = response.data;
                    
                    await db.transaction('rw', db.clients, db.movimientos, async () => {
                        await db.movimientos.where('cliente_id').equals(localClient.id).modify({ cliente_id: serverClient.id });
                        await db.clients.delete(localClient.id);
                        await db.clients.add({ ...serverClient, needsSync: 0 });
                    });
                    console.log(`Cliente "${localClient.nombre}" creado en servidor (ID: ${serverClient.id})`);
                } catch (error) { console.error(`Error sincronizando creación de cliente ${localClient.id}:`, error); }
            }
        }

        // --- 2. SINCRONIZACIÓN DE CLIENTES ACTUALIZADOS (needsSync: 2) ---
        const clientsToUpdate = await db.clients.where('needsSync').equals(2).toArray();
        if (clientsToUpdate.length > 0) {
            console.log(`Enviando ${clientsToUpdate.length} actualizaciones de clientes...`);
            for (const localClient of clientsToUpdate) {
                try {
                    const payload = {
                        nombre: localClient.nombre,
                        telefono: localClient.telefono,
                        ubicacion_aproximada: localClient.ubicacion_aproximada,
                        comentario: localClient.comentario,
                        estado_cliente: localClient.estado_cliente
                    };
                    await api.updateClient(localClient.id, payload);
                    await db.clients.update(localClient.id, { needsSync: 0 });
                    console.log(`Cliente "${localClient.nombre}" actualizado en servidor.`);
                } catch (error) { console.error(`Error sincronizando actualización de cliente ${localClient.id}:`, error); }
            }
        }

        // --- 3. SINCRONIZACIÓN DE CLIENTES ELIMINADOS (needsSync: 3) ---
        const clientsToDelete = await db.clients.where('needsSync').equals(3).toArray();
        if (clientsToDelete.length > 0) {
            console.log(`Enviando ${clientsToDelete.length} eliminaciones de clientes...`);
            for (const localClient of clientsToDelete) {
                try {
                    // Solo intentamos eliminar si el ID es positivo (ya existe en el servidor)
                    if (localClient.id > 0) {
                        await api.deleteClient(localClient.id);
                    }
                    // Después de confirmar con el servidor (o si era un cliente local), lo borramos permanentemente
                    await db.clients.delete(localClient.id);
                    console.log(`Cliente "${localClient.nombre}" eliminado del servidor y localmente.`);
                } catch (error) { console.error(`Error sincronizando eliminación de cliente ${localClient.id}:`, error); }
            }
        }

        // 4. Lógica para sincronizar movimientos individuales
        const movementsToSync = await db.movimientos.where('needsSync').equals(1).toArray();
        
        if (movementsToSync.length > 0) {
            console.log(`Enviando ${movementsToSync.length} movimientos nuevos al servidor...`);

            for (const localMovement of movementsToSync) {
                try {
                    // Si el cliente_id es negativo, significa que el cliente al que pertenece
                    // todavía no se ha sincronizado. Debemos esperar a la siguiente ronda.
                    if (localMovement.cliente_id < 0) {
                        console.log(`Saltando movimiento ${localMovement.id}, su cliente aún no está sincronizado.`);
                        continue; // Pasa al siguiente movimiento
                    }

                    // Preparamos el payload que espera la API
                    const payload = {
                        monto: localMovement.monto
                        // Tu API de movimientos parece que solo necesita el monto,
                        // ya que el tipo se deduce del signo y el resto se calcula en el backend.
                        // Si necesitara más campos, se añadirían aquí.
                    };

                    // Enviamos el movimiento al servidor
                    await api.createMovement(localMovement.cliente_id, payload);

                    // Si tuvo éxito, lo borramos de la base de datos local.
                    // Lo borramos en lugar de solo actualizar 'needsSync' porque la sincronización
                    // inicial (Remoto -> Local) es la que debe traer la versión "oficial" del movimiento.
                    // Esto evita duplicados y conflictos.
                    await db.movimientos.delete(localMovement.id);

                    console.log(`Movimiento ${localMovement.id} para cliente ${localMovement.cliente_id} sincronizado y eliminado localmente.`);

                } catch (error) {
                    console.error(`Error sincronizando movimiento ${localMovement.id}:`, error);
                }
            }
        } else {
            console.log('No hay nuevos movimientos para sincronizar.');
        }

        console.log('✅ Proceso de sincronización terminado.');
    } catch (error) {
        console.error('Error durante el ciclo de sincronización:', error);
    } finally {
        isSyncing = false;
    }
};


export const initSyncService = () => {
    // Listener del evento 'online' como primer intento
    window.addEventListener('online', () => {
        console.log('Evento "online" detectado. Intentando sincronizar...');
        syncData();
    });
    window.addEventListener('offline', () => {
        console.log('Modo offline detectado.');
    });

    // Verificación Periódica (la parte clave)
    const startPeriodicSync = () => {
        // Si ya hay un intervalo corriendo, no creamos otro
        if (syncIntervalId) return;

        console.log('Iniciando verificación periódica de sincronización (cada 30 segundos)...');
        // Intentamos sincronizar cada 30 segundos
        syncIntervalId = setInterval(syncData, 30000); 
    };

    // Al cargar la app, iniciamos la verificación periódica
    startPeriodicSync();
    
    // Intento inicial por si acaso
    syncData();

    console.log('Servicio de Sincronización Inicializado.');
};
