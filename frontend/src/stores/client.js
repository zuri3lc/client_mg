import { defineStore } from "pinia";
import api from '@/services/api';
import { db } from '@/services/db';
import { ref } from "vue";
import { useAuthStore } from './auth';

export const useClientStore = defineStore('client', () =>{
    const clients = ref([]); // estado para mantener los clientes en la memoria
    const selectedClient = ref(null);
    //preservacion de busqueda
    const searchQuery = ref('');

    const initialSync = async () => {
        try {
            console.log('Iniciando sincronización inicial...');
            const [clientsResponse, movementsResponse] = await Promise.all([
                api.getClients(),
                api.getAllMoves(),
            ]);

            await db.clients.bulkPut(clientsResponse.data);
            await db.movimientos.bulkPut(movementsResponse.data);

            console.log(`Sincronización inicial completada... ${clientsResponse.data.length} clientes y ${movementsResponse.data.length} movimientos sincronizados}`);
        } catch (error) {
            console.error('Error al realizar la sincronización inicial:', error);
            throw error;
        }
};

    const loadClients = async () => {
        try{
            const allLocalClients = await db.clients.toArray();
            
            const activeClients = allLocalClients.filter(client => client.needsSync !== 3);

            activeClients.sort((a, b) => a.nombre.localeCompare(b.nombre));
            clients.value = activeClients;

            console.info(`Cargados ${activeClients.length} clientes locales`);
        } catch (error){
            console.error('Error al cargar clientes locales desde Dexie:', error);
            clients.value = [];
        }
    };
    
    const addClient = async (clientData) => {
    const authStore = useAuthStore();
    const tempClientId = -Date.now();

    const newClient = {
        id: tempClientId,
        nombre: clientData.nombre,
        telefono: clientData.telefono,
        ubicacion_aproximada: clientData.ubicacion,
        comentario: clientData.comentario,
        saldo_actual: clientData.saldo_inicial || 0.00,
        estado_cliente: 'regular',
        fecha_adquisicion: new Date().toISOString().split('T')[0],
        usuario_sistema_id: authStore.user.id,
        needsSync: 1
    };

    const initialMovement = {
        id: -Date.now() + 1, // ID temporal ligeramente diferente
        cliente_id: tempClientId,
        fecha_movimiento: new Date().toISOString().split('T')[0],
        tipo_movimiento: 'deuda_inicial',
        monto: clientData.saldo_inicial || 0.00,
        saldo_anterior: 0.00,
        saldo_final: clientData.saldo_inicial || 0.00,
        usuario_sistema_id: authStore.user.id,
        needsSync: 1 // También necesita sincronizarse
    };

    try {
        await db.transaction('rw', db.clients, db.movimientos, async () => {
            await db.clients.add(newClient);
            await db.movimientos.add(initialMovement);
        });
        // await loadClients();
        // clients.value.unshift(newClient);
        clients.value.push(newClient);
        clients.value.sort((a, b) => a.nombre.localeCompare(b.nombre));
        console.log('Cliente y movimiento inicial guardados localmente.');
    } catch (error) {
        console.error('Error al guardar cliente y movimiento inicial:', error);
        throw error;
    }
};

    const fetchClientById = async (id) => {
        try {
            const client = await db.clients.get(id);
            if (client) {
                selectedClient.value = client;
            } else {
                console.error(`No se encontró el cliente con ID: ${id}`);
                selectedClient.value = null;
            }
        } catch (error) {
            console.error('Error al buscar cliente por ID:', error);
            selectedClient.value = null;
        }
    };

    const updateClient = async (clientId, updateData) => {
        try {
            const payload =  {
                nombre: updateData.nombre,
                telefono: updateData.telefono,
                ubicacion_aproximada: updateData.ubicacion,
                comentario: updateData.comentario,
                estado_cliente: updateData.estado,
                // Marca '2' para diferenciar una actualización de una nueva creación ('1').
                needsSync: 2 
            };
            await db.clients.update(clientId, payload);
            console.log('Cliente actualizado localmente.');
            if (selectedClient.value && selectedClient.value.id === clientId) {
                Object.assign(selectedClient.value, payload);
            }
        } catch (error) {
            console.error('Error al actualizar cliente localmente:', error);
            throw error;
        }
    }

    const markClientForDeletion = async (clientId) => {
        try {
            const payload = {
                needsSync: 3 // Marca para eliminación
            };
            await db.clients.update(clientId, payload);
            console.log('Cliente marcado para eliminación localmente.');
            clients.value = clients.value.filter(c => c.id !== clientId); 
        } catch (error){
            console.error("Error al marcar cliente para eliminación localmente:", error);
            throw error;
        }
    };



    return { 
        clients,
        selectedClient,
        searchQuery,
        initialSync,
        loadClients,
        addClient,
        fetchClientById,
        updateClient,
        markClientForDeletion
    };
});