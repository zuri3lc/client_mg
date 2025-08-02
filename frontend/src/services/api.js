import { useAuthStore } from "@/stores/auth";
import axios from "axios";

//Creando una instancia de axios con la configuracion base
const apiClient = axios.create({
    baseURL: 'https://api.techz.bid',
    headers: {
        'Content-Type': 'application/json',
    
    }
});

// INTERCEPTOR para añadir el token a las peticiones
apiClient.interceptors.request.use(config =>{
    const authStore = useAuthStore();
    const token = authStore.token;
    if(token){
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, error => {
    return Promise.reject(error);
})

// Exportamos un objeto con los metodos
export default {
    login(credentials){
        // Pasamos a axios el formato que requiere
        const formData = new URLSearchParams();
        formData.append('username', credentials.username);
        formData.append('password', credentials.password);

        return apiClient.post('/auth/login', formData, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        });
    },
    register(userData){
        return apiClient.post('/auth/register', userData);
    },
    getClients(){
        return apiClient.get('/clients');
    },
    getAllMoves(){
        return apiClient.get("movs/all")
    },
    createClient(clientData) {
        return apiClient.post('/clients/', clientData);
    },
    updateClient(clientId, clientData) {
        return apiClient.put(`/clients/${clientId}`, clientData);
    },
    deleteClient(clientId) {
        return apiClient.delete(`/clients/${clientId}`);
    },
    createMovement(clientId, movementData) {
        return apiClient.post(`/clients/${clientId}/movements`, movementData);
    },
    pingServer(){
        return apiClient.get('/');
    }
    // Aqui se añaden las demas llamadas
}