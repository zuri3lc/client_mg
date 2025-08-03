import { defineStore } from "pinia";
import { ref } from "vue";
import api from "@/services/api";
import { db } from "@/services/db";

// defineStore crea el almacen
export const useAuthStore = defineStore("auth", () => {
    //--- STATE ---
    // guardamos el token y datos del usuario
    const accessToken = ref(localStorage.getItem("accessToken"));
    const refreshToken = ref(localStorage.getItem("refreshToken"));
    const user = ref(JSON.parse(localStorage.getItem("user")));

    //--- ACTIONS ---
    // --- manejo del login ---
    const login = async (credentials) => {
        const response = await api.login(credentials);
        // guardamos el token y los datos en el estado
        accessToken.value = response.data.access_token;
        refreshToken.value = response.data.refresh_token;
        user.value = {username: credentials.username, id: response.data.user_id};
        // guardamos en localStorage para persistir la sesion
        localStorage.setItem('accessToken', accessToken.value);
        localStorage.setItem('refreshToken', refreshToken.value);
        localStorage.setItem('user', JSON.stringify(user.value));
    };

    const logout = async () => { // La convertimos en async
        try {
            // 1. Verificamos si hay algún elemento pendiente de sincronizar en CUALQUIER tabla.
            const pendingClients = await db.clients.where('needsSync').above(0).count();
            const pendingMovements = await db.movimientos.where('needsSync').above(0).count();
            const itemsPending = pendingClients + pendingMovements;

            if (itemsPending > 0) {
                // Si hay pendientes, NO borramos la DB.
                console.log(`Logout realizado, pero ${itemsPending} elementos siguen pendientes de sincronización. La base de datos local se mantiene intacta.`);
            } else {
                // Si no hay pendientes, borramos todo.
                console.log("Cerrando sesión y limpiando base de datos local...");
                await db.clients.clear();
                await db.movimientos.clear();
            }
        } catch (error) {
            console.error("Error durante el proceso de logout:", error);
        } finally {
            // 2. La limpieza de la sesión (token y user) se hace SIEMPRE.
            accessToken.value = null;
            refreshToken.value = null;
            user.value = null;
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('user');
        }
    };

    const refreshAccessToken = async () => {
        if (!refreshToken.value){
            throw new Error("No hay refresh token disponible");
        } try {
            const response =  await api.refreshToken(refreshToken.value);
            accessToken.value = response.data.access_token;
            refreshToken.value = response.data.refresh_token;
            
            localStorage.setItem('accessToken', accessToken.value);
            localStorage.setItem('refreshToken', refreshToken.value);
            
            return accessToken.value;
        } catch (error) {
            console.error("Error al refrescar el token:", error);
            await logout();
            throw error;
        }
    }

    //--- GETERS ---
    //Exponemos el estado
    return {accessToken, refreshToken, user, login, logout, refreshAccessToken };
});
