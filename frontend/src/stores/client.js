import { defineStore } from "pinia";
import api from '@/services/api';
import { db } from '@/services/db';
import { ref } from "vue";
import { useAuthStore } from './auth';

export const useClientStore = defineStore('client', () =>{
    const clients = ref([]); // estado para mantener los clientes en la memoria
    const selectedClient = ref(null);

    //buscamos los clientes en el servidor y los guardamos localmente
    const fetchStoreClients = async () => {
        try{
            console.log('Descargando base de datos...');
            const response = await api.getClients();
            const remoteClients = response.data;
            
            //BulkPut para añadir o remplazar los clientes
            // solo descarga inicial
            await db.clients.bulkPut(remoteClients);
            clients.value = remoteClients;
            console.log(`${remoteClients.length} clientes guardados localmente`);
        } catch (error){
            console.error('Error al sincronizar clientes:', error);
            throw error;
        }
    };
    const loadClients = async () => {
        try{
            const localClients = await db.clients.toArray();
            clients.value = localClients;
            console.error(`Cargados ${localClients.length} clientes locales`);
        } catch (error){
            console.error('Error al cargar clientes locales desde Dexie:', error);
            clients.value = [];
        }
    };
    const addClient = async(clientData) => {
        const authStore = useAuthStore();
        const newClient = {
            //id negativo, temporal para nuestra db
            id: -Date.now(),
            nombre: clientData.nombre,
            telefono: clientData.telefono,
            ubicacion_aproximada: clientData.ubicacion,
            comentario: clientData.comentario,
            saldo_actual: clientData.saldo_inicial ||0.00,
            estado_cliente: 'regular',
            fecha_adquisicion: new Date().toISOString().split('T')[0],
            usuario_sistema_id: authStore.user.id,
            needsSync: 1
        };
        try{
            await db.clients.add(newClient);
            console.log('Cliente local agregado')
            await loadClients();
    } catch(error){
        console.error('Error al agregar cliente local:', error);
        throw error
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

    return { 
        clients,
        selectedClient,
        fetchStoreClients,
        loadClients, addClient,
        fetchClientById 
    };
});