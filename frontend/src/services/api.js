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
    // access token para las peticiones normales
    const token = authStore.accessToken;
    if(token){
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, error => {
    return Promise.reject(error);
});

// --- INTERCEPTOR DE RESPUESTA (Response) ---
// Se ejecuta DESPUÉS de recibir una respuesta (exitosa o con error).
apiClient.interceptors.response.use(
    (response) => response, // Si la respuesta es exitosa (2xx), la devuelve sin más.
    async (error) => {
        const originalRequest = error.config;
        // Si el error es 401 (No Autorizado) y no hemos reintentado ya esta petición
        if (error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true; // Marcamos que vamos a reintentar
            
            const authStore = useAuthStore();
            try {
                // Intentamos refrescar el token
                const newAccessToken = await authStore.refreshAccessToken();
                // Actualizamos el header de la petición original con el nuevo token
                originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
                // Reintentamos la petición original que había fallado
                return apiClient(originalRequest);
            } catch (refreshError) {
                // Si el refresco falla, el store ya se encarga de hacer logout.
                // Rechazamos la promesa para detener cualquier otra acción.
                return Promise.reject(refreshError);
            }
        }
        // Para cualquier otro error, simplemente lo devolvemos.
        return Promise.reject(error);
    }
);

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
    refreshToken(token){
        return axios.post('https://api.techz.bid/auth/refresh', {}, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
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