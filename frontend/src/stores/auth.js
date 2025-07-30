import { defineStore } from "pinia";
import { ref } from "vue";
import api from "@/services/api";

// defineStore crea el almacen
export const useAuthStore = defineStore("auth", () => {
    //--- STATE ---
    // guardamos el token y datos del usuario
    const token = ref(localStorage.getItem("token"));
    const user = ref(JSON.parse(localStorage.getItem("user")));

    //--- ACTIONS ---
    // --- manejo del login ---
    const login = async (credentials) => {
        const response = await api.login(credentials);
        // guardamos el token y los datos en el estado
        token.value = response.data.access_token;
        user.value = {username: credentials.username, id: response.data.user_id};
        // guardamos en localStorage para persistir la sesion
        localStorage.setItem('token', token.value);
        localStorage.setItem('user', JSON.stringify(user.value));
    };

    //--- MANEJO LOGOUT ---
    const logout = () => {
        token.value = null;
        user.value = null;
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    };
    //--- GETERS ---
    //Exponemos el estado
    return { token, user, login, logout };
});
