import { defineStore } from "pinia";
import { ref } from "vue";
import api from "@/services/api";
import { db } from "@/services/db";
import { useUIStore } from "./ui";

// defineStore crea el almacen
export const useAuthStore = defineStore("auth", () => {
    //--- STATE ---
    const accessToken = ref(localStorage.getItem("accessToken"));
    // const refreshToken = ref(localStorage.getItem("refreshToken"));
    const user = ref(JSON.parse(localStorage.getItem("user")));

    //--- ACTIONS ---
    // --- manejo del login ---
    const login = async (credentials) => {
        const response = await api.login(credentials);
        accessToken.value = response.data.access_token;
        // refreshToken.value = response.data.refresh_token;
        user.value = {username: credentials.username, id: response.data.user_id};
        localStorage.setItem('accessToken', accessToken.value);
        // localStorage.setItem('refreshToken', refreshToken.value);
        localStorage.setItem('user', JSON.stringify(user.value));
    };

    // const logout = async () => {
    //     const uiStore = useUIStore();

    //     try {
    //         const pendingClients = await db.clients.where('needsSync').above(0).count();
    //         const pendingMovements = await db.movimientos.where('needsSync').above(0).count();
    //         const itemsPending = pendingClients + pendingMovements;

    //         if (itemsPending > 0) {
    //             const confirmed = await uiStore.confirmLogout();
    //             if (!confirmed) {
    //                 console.log("Logout cancelado por el usuario.");
    //                 return;
    //             }
    //             console.log(`Logout realizado, pero ${itemsPending} elementos siguen pendientes de sincronización. La base de datos local se mantiene intacta.`);
    //         } else {
    //             console.log("Cerrando sesión y limpiando base de datos local...");
    //             await db.clients.clear();
    //             await db.movimientos.clear();
    //         }

    //         accessToken.value = null;
    //         // refreshToken.value = null;
    //         user.value = null;
    //         localStorage.removeItem('accessToken');
    //         // localStorage.removeItem('refreshToken');
    //         localStorage.removeItem('user');

    //         window.location.href = '/login';

    //     } catch (error) {
    //         console.error("Error durante el proceso de logout:", error);
    //         accessToken.value = null;
    //         user.value = null;
    //         localStorage.removeItem('accessToken');
    //         localStorage.removeItem('user');
    //         window.location.href = '/login';
    //     }
    // };

    const logout = async () => {
        const uiStore = useUIStore();
        try {
            const pendingClients = await db.clients.where('needsSync').above(0).count();
            const pendingMovements = await db.movimientos.where('needsSync').above(0).count();
            const itemsPending = pendingClients + pendingMovements;

            let canProceed = false;

            // 1. Decidimos si podemos proceder
            if (itemsPending === 0) {
                // Si no hay nada pendiente, podemos proceder sin preguntar
                canProceed = true;
            } else {
                // Si hay pendientes, preguntamos al usuario
                const userConfirmed = await uiStore.confirmLogout();
                if (userConfirmed) {
                    // El usuario confirmó, podemos proceder
                    canProceed = true;
                } else {
                    // El usuario canceló, no hacemos nada más.
                    console.log('Logout cancelado por el usuario.');
                    return;
                }
            }

            // 2. Si podemos proceder, ejecutamos el cierre de sesión
            if (canProceed) {
                console.log("Procediendo con el cierre de sesión...");
                
                // 3. Volvemos a verificar si debemos limpiar la DB
                if (itemsPending === 0) {
                    console.log("No hay datos pendientes, limpiando la base de datos local.");
                    await db.clients.clear();
                    await db.movimientos.clear();
                } else {
                    // Esto se ejecutará si el usuario confirmó el logout con datos pendientes
                    console.log("Hay datos pendientes, la base de datos local se mantendrá intacta.");
                }

                // 4. Finalmente, siempre limpiamos la sesión
                accessToken.value = null;
                user.value = null;
                localStorage.removeItem('accessToken');
                localStorage.removeItem('user');
                
                window.location.href = '/login';
            }
        } catch (error) {
            console.error("Error durante el proceso de logout:", error);
        }
    };

    //--- GETERS ---
    //Exponemos el estado
    return {accessToken, user, login, logout, };
});
