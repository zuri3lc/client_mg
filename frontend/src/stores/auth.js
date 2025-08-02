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
    // const logout = () => {
    //     token.value = null;
    //     user.value = null;
    //     localStorage.removeItem('token');
    //     localStorage.removeItem('user');
    // };
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
            token.value = null;
            user.value = null;
            localStorage.removeItem('token');
            localStorage.removeItem('user');
        }
    };

    //--- GETERS ---
    //Exponemos el estado
    return { token, user, login, logout };
});
