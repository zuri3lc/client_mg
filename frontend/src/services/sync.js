import { db } from './db';
import api from './api';
import { useClientStore } from '@/stores/client';
import { useMovimientoStore } from '@/stores/movimiento';
import { Network } from '@capacitor/network'; // Importar Network

let isSyncing = false;
let syncIntervalId = null;

//--- Descarga de datos desde el servidor ---
export const downloadDataFromServer = async () => {
    // ... (sin cambios en downloadDataFromServer)
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
        throw error; // Re-lanzar error para manejo superior
    }
};

//--- Sincronizacion completa ---
// Agregamos parametro force para evitar chequeos redundantes si ya sabemos que hay red (ej. login)
export const syncData = async (force = false) => {
    const clientStore = useClientStore();
    const movimientoStore = useMovimientoStore();

    if (isSyncing) {
        console.log('⚠️ Sincronización en curso, se omite nueva solicitud.');
        return;
    }

    // Verificación de red más robusta con Capacitor
    const networkStatus = await Network.getStatus();
    const isOnline = force ? true : (networkStatus.connected && navigator.onLine);

    if (!isOnline) {
        console.log('📴 Offline detectado (Network plugin o navigator), se omite sincronización.');
        return;
    }

    try {
        if (!force) {
            await api.pingServer();
            console.log('✅ Conexión con el servidor confirmada.');
        } else {
            console.log('⏩ Modo forzado: Saltando ping de verificación.');
        }
    } catch (error) {
        console.log('⚠️ No se pudo conectar con el servidor. Se aborta la sincronización.');
        // Si es forzado (login), tal vez deberíamos intentar igual o lanzar error, 
        // pero por seguridad abortamos si el ping falla salvo que queramos arriesgarnos.
        // En este caso, si falla el ping, es mejor abortar para no bloquear la UI con timeouts largos
        if (!force) return;
        console.warn('⚠️ Ping falló pero se fuerza la sincronización...');
    }

    isSyncing = true;
    console.log('🚀 Iniciando proceso de sincronización...');

    try {

        const clientsToCreateCount = await db.clients.where('needsSync').equals(1).count();
        const clientsToUpdateCount = await db.clients.where('needsSync').equals(2).count();
        const clientsToDeleteCount = await db.clients.where('needsSync').equals(3).count();
        const movementsToSyncCount = await db.movimientos.where('needsSync').equals(1).count();
        const hasLocalChanges = clientsToCreateCount + clientsToUpdateCount + clientsToDeleteCount + movementsToSyncCount > 0;


        if (!hasLocalChanges) {
            console.log('No hay cambios locales para sincronizar.');
        } else {
            console.log('Detectados cambios locales. Comenzando sincronización')
        }
        
        // --- PASO 2: Subir los cambios locales al servidor (Sync Up) ---

        // Subir nuevos clientes
        if (clientsToCreateCount > 0) {
            const clientsToCreate = await db.clients.where('needsSync').equals(1).toArray();
            console.log(`Enviando ${clientsToCreate.length} clientes nuevos...`);
            for (const localClient of clientsToCreate) {
                const tempId = localClient.id;
                try {
                    const payload = {
                        nombre: localClient.nombre,
                        telefono: localClient.telefono,
                        ubicacion_aproximada: localClient.ubicacion_aproximada,
                        comentario: localClient.comentario,
                        estado_cliente: localClient.estado_cliente,
                        saldo_inicial: localClient.saldo_actual,
                        fecha_adquisicion: localClient.fecha_adquisicion
                    };
                    const response = await api.createClient(payload);
                    const serverId = response.data.id;
                    

                    await db.transaction('rw', db.clients, db.movimientos, async () => {
                    // 1. Actualiza el cliente local con el ID del servidor.
                    await db.clients.update(tempId, { id: serverId, needsSync: 0 });

                    // 2. Busca los movimientos asociados al ID temporal.
                    const movementsToUpdate = await db.movimientos.where('cliente_id').equals(tempId).toArray();
                    
                    for (const mov of movementsToUpdate) {
                        // 3. Borramos el 'deuda_inicial' local porque el backend ya lo creó.
                        if (mov.tipo_movimiento === 'deuda_inicial') {
                            await db.movimientos.delete(mov.id);
                        } else {
                            // 4. A los demás movimientos, les ponemos el nuevo ID del servidor.
                            await db.movimientos.update(mov.id, { cliente_id: serverId });
                        }
                    }
                });
                console.log(`Cliente con ID temporal ${tempId} actualizado a ID de servidor ${serverId}.`);
                    console.log(`Cliente "${localClient.nombre}" creado en servidor (ID: ${serverId})`);
                } catch (error) { 
                    console.error(`Error sincronizando creación de cliente ${localClient.id}:`, error);
                    console.error(`Error al sincronizar cliente nuevo con ID temporal ${tempId}:`, error);
                }
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

        const movementsToCreate = await db.movimientos.where('needsSync').equals(1).toArray();
            if (movementsToCreate.length > 0) {
            console.log(`Sincronizando ${movementsToCreate.length} movimientos nuevos...`);
            for (const mov of movementsToCreate) {
            try {
                if (mov.cliente_id < 0) { 
                    console.warn(`Saltando movimiento ${mov.id} porque su cliente (ID: ${mov.cliente_id}) aún no está sincronizado.`);
                    continue;
                }
                
                const payload = {
                    monto: mov.monto,
                    fecha_movimiento: mov.fecha_movimiento
                };

                await api.createMovement(mov.cliente_id, payload);
                await db.movimientos.update(mov.id, { needsSync: 0 });

            } catch (error) {
                console.error(`Error al sincronizar movimiento nuevo con ID ${mov.id}:`, error);
            }
        }
    }

        
        // --- PASO 3: Descargar los datos actualizados del servidor (Sync Down) ---
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
        
        console.log('Actualizando datos locales desde el servidor...')
        await downloadDataFromServer();
    } catch (error) {
        console.error('Error durante el ciclo de sincronización:', error);
        throw error; // Re-lanzar para que autoSync maneje el estado de error
    } finally {
        isSyncing = false;
        console.log('✅ Proceso de sincronización terminado.');
    }
};

// export const initSyncService = () => {
//     // Listener del evento 'online' como primer intento
//     window.addEventListener('online', () => {
//         console.log('Evento "online" detectado. Intentando sincronizar...');
//         syncData();
//     });
//     window.addEventListener('offline', () => {
//         console.log('Modo offline detectado.');
//     });

//     const startPeriodicSync = () => {
//         if (syncIntervalId) return;
//         console.log('Iniciando verificación periódica de sincronización (cada 30 segundos)...');
//         syncIntervalId = setInterval(syncData, 30000); 
//     };
    
//     startPeriodicSync();
//     syncData();
//     console.log('Servicio de Sincronización Inicializado.');
// };

