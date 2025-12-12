import router from '@/router'; // Importar router
import { useAuthStore } from "@/stores/auth";
import axios from "axios";

//Creando una instancia de axios con la configuracion base
// const apiClient = axios.create({
//     baseURL: 'https://api.techz.bid',
//     headers: {
//         'Content-Type': 'application/json',    
//     }
// });

const API_BASE_URL =  import.meta.env.VITE_API_URL || 'https://api.techz.bid'

const apiClient = axios.create({
    baseURL: API_BASE_URL,
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

// apiClient.interceptors.response.use(
//     (response) => response, 
//     async (error) => {
//         const originalRequest = error.config;
        
//         // Si el error es 401 (No Autorizado)
//         if (error.response.status === 401 && !originalRequest._retry) {
//             originalRequest._retry = true; // Evitar bucles infinitos
            
//             const authStore = useAuthStore();
//             console.error("Token expirado o inválido. Cerrando sesión.");
            
//             // En lugar de refrescar, directamente cerramos la sesión
//             await authStore.logout();
            
//             // Opcional: Redirigir al login
//             // Esto es mejor manejarlo en la UI, pero se puede hacer aquí también.
//             window.location.href = '/login'; 
            
//             // Rechazamos la promesa para detener la petición original
//             return Promise.reject(error); 
//         }

//         return Promise.reject(error);
//     }
// );

apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
    if (error.response) {
        const { status, config } = error.response;

        if (status === 401 && !config.url.includes('/auth/login')) {
        const authStore = useAuthStore();
        console.log('Token no válido o expirado. Se cerrará la sesión.');
        await authStore.logout();
        // Redirección suave
        router.push('/login');
        }
    } else {
        console.error('Error de red detectado:', error.message);
    }
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
    // refreshToken(token){
    //     return axios.post('https://api.techz.bid/auth/refresh', {}, {
    //         headers: {
    //             'Authorization': `Bearer ${token}`
    //         }
    //     })
    // },
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