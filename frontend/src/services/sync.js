// src/services/sync.js
import { db } from './db';
import api from './api';
import { useClientStore } from '@/stores/client';
import { useMovimientoStore } from '@/stores/movimiento';

let isSyncing = false;
let syncIntervalId = null;

//--- Descarga de datos desde el servidor ---
export const downloadDataFromServer = async () => {
    const clientStore = useClientStore();
    const movimientoStore = useMovimientoStore();

    console.log('📥 Iniciando descarga de datos desde el servidor...');
    try{
        const selectedClientId = clientStore.selectedClient ? clientStore.selectedClient.id : null;
        const [clientsResponse, movementsResponse] = await Promise.all([
            api.getClients(),
            api.getAllMoves(),
        ]);
        await db.transaction('rw', db.clients, db.movimientos, async () => {
            await db.clients.clear();
            await db.clients.bulkPut(clientsResponse.data);
            await db.movimientos.clear();
            await db.movimientos.bulkPut(movementsResponse.data);
        });
        await clientStore.loadClients();
        
        if(selectedClientId){
            await clientStore.fetchClientById(selectedClientId);
            if (clientStore.selectedClient){
                await movimientoStore.loadMovimientosFromDB(selectedClientId);
            }
        }
        console.log('✅ Datos descargados con éxito desde el servidor.');
    }catch(error){
        console.error('Error al descargar datos desde el servidor:', error);
    }
};

//--- Sincronizacion completa ---
export const syncData = async () => {
    const clientStore = useClientStore();
    const movimientoStore = useMovimientoStore();

    if (isSyncing || !navigator.onLine) {
        if (!navigator.onLine) console.log('Offline, se omite el intento de sincronización.');
        return;
    }

    try {
        await api.pingServer();
        console.log('✅ Conexión con el servidor confirmada.');
    } catch (error) {
        console.log('⚠️ No se pudo conectar con el servidor. Se aborta la sincronización.');
        return;
    }

    isSyncing = true;
    console.log('🚀 Iniciando proceso de sincronización...');

    try {
        let needsRefresh = false;

        const clientsToCreateCount = await db.clients.where('needsSync').equals(1).count();
        const clientsToUpdateCount = await db.clients.where('needsSync').equals(2).count();
        const clientsToDeleteCount = await db.clients.where('needsSync').equals(3).count();
        const movementsToSyncCount = await db.movimientos.where('needsSync').equals(1).count();

        if (clientsToCreateCount + clientsToUpdateCount + clientsToDeleteCount + movementsToSyncCount === 0) {
            console.log('No hay cambios locales para sincronizar.');
            isSyncing = false;
            return;
        }
        
        needsRefresh = true;

        // --- PASO 2: Subir los cambios locales al servidor (Sync Up) ---

        // Subir nuevos clientes
        if (clientsToCreateCount > 0) {
            const clientsToCreate = await db.clients.where('needsSync').equals(1).toArray();
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
                        await db.movimientos.where('cliente_id').equals(localClient.id).modify({ cliente_id: serverClient.id, needsSync: 0 });
                        await db.clients.delete(localClient.id);
                        await db.clients.add({ ...serverClient, needsSync: 0 });
                    });
                    console.log(`Cliente "${localClient.nombre}" creado en servidor (ID: ${serverClient.id})`);
                } catch (error) { console.error(`Error sincronizando creación de cliente ${localClient.id}:`, error); }
            }
        }

        // Subir clientes actualizados
        if (clientsToUpdateCount > 0) {
            const clientsToUpdate = await db.clients.where('needsSync').equals(2).toArray();
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

        // Subir clientes eliminados
        if (clientsToDeleteCount > 0) {
            const clientsToDelete = await db.clients.where('needsSync').equals(3).toArray();
            console.log(`Enviando ${clientsToDelete.length} eliminaciones de clientes...`);
            for (const localClient of clientsToDelete) {
                try {
                    if (localClient.id > 0) {
                        await api.deleteClient(localClient.id);
                    }
                    await db.clients.delete(localClient.id);
                    console.log(`Cliente "${localClient.nombre}" eliminado del servidor y localmente.`);
                } catch (error) { console.error(`Error sincronizando eliminación de cliente ${localClient.id}:`, error); }
            }
        }

        // Subir nuevos movimientos
        if (movementsToSyncCount > 0) {
            const movementsToSync = await db.movimientos.where('needsSync').equals(1).toArray();
            console.log(`Enviando ${movementsToSync.length} movimientos nuevos...`);
            for (const localMovement of movementsToSync) {
                try {
                    if (localMovement.cliente_id < 0) continue;
                    const payload = { monto: localMovement.monto };
                    await api.createMovement(localMovement.cliente_id, payload);
                    await db.movimientos.update(localMovement.id, { needsSync: 0 });
                    console.log(`Movimiento ${localMovement.id} sincronizado.`);
                } catch (error) {
                    console.error(`Error sincronizando movimiento ${localMovement.id}:`, error);
                }
            }
        }
        
        // --- PASO 3: Descargar los datos actualizados del servidor (Sync Down) ---
        if (needsRefresh) {
            console.log('Sincronización Local->Remoto completada. Actualizando datos desde el servidor...');
            try {
                const selectedClientId = clientStore.selectedClient ? clientStore.selectedClient.id : null;

                const [clientsResponse, movementsResponse] = await Promise.all([
                    api.getClients(),
                    api.getAllMoves(),
                ]);

                await db.transaction('rw', db.clients, db.movimientos, async () => {
                    await db.clients.clear();
                    await db.clients.bulkPut(clientsResponse.data);
                    await db.movimientos.clear();
                    await db.movimientos.bulkPut(movementsResponse.data);
                });
                
                await clientStore.loadClients();

                if (selectedClientId) {
                    await clientStore.fetchClientById(selectedClientId);
                    if (clientStore.selectedClient) {
                        await movimientoStore.loadMovimientosFromDB(selectedClientId);
                    }
                }
                console.log('Datos locales actualizados con la información del servidor.');

            } catch (error) {
                console.error('Error al refrescar los datos desde el servidor:', error);
            }
        }
        await downloadDataFromServer();
    } catch (error) {
        console.error('Error durante el ciclo de sincronización:', error);
    } finally {
        isSyncing = false;
        console.log('✅ Proceso de sincronización terminado.');
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

    const startPeriodicSync = () => {
        if (syncIntervalId) return;
        console.log('Iniciando verificación periódica de sincronización (cada 30 segundos)...');
        syncIntervalId = setInterval(syncData, 30000); 
    };
    
    startPeriodicSync();
    syncData();
    console.log('Servicio de Sincronización Inicializado.');
};

