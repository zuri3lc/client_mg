import axios from "axios";

//Creando una instancia de axios con la configuracion base
const apiClient = axios.create({
    baseURL: 'https://api.techz.bid',
    headers: {
        'Content-Type': 'application/json',
    
    }
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
    }
    // Aqui se añaden las demas llamadas
}