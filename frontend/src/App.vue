<script setup>
import { RouterView, useRouter, useRoute } from 'vue-router'
import GlobalFeedback from './components/GlobalFeedback.vue';
import { onMounted } from 'vue';
import { startAutoSyncService } from '@/services/autoSync';
import { App } from '@capacitor/app';
import { useUIStore } from '@/stores/ui';
import { SplashScreen } from '@capacitor/splash-screen'; // Importar Splash Screen

const router = useRouter();
const route = useRoute();
const uiStore = useUIStore();

let lastBackTime = 0; // Para controlar el doble toque

onMounted(async () => {
    // Iniciamos el servicio silencioso
    startAutoSyncService();

    try {
        // Ocultamos el Splash Screen una vez que Vue ha montado la app
        await SplashScreen.hide();
    } catch (e) {
        console.warn('No se pudo ocultar el Splash Screen:', e);
    }

    // Lógica del botón ATRÁS
    App.addListener('backButton', ({ canGoBack }) => {
        // Rutas donde queremos que el botón "Atrás" intente salir/minimizar
        const rootRoutes = ['home', 'login']; 
        const currentName = route.name;

        if (rootRoutes.includes(currentName)) {
            const now = Date.now();
            // Si el toque fue hace menos de 2 segundos (2000ms)
            if (now - lastBackTime < 2000) {
                // Confirmado: Minimizar la app (No matarla)
                App.minimizeApp();
            } else {
                // Primer toque: Mostrar advertencia
                lastBackTime = now;
                uiStore.showSnackbar('Toca otra vez para salir', 'info');
            }
        } else {
            // En cualquier otra ruta, comportamiento normal
            if (canGoBack) {
                router.back();
            } else {
                // Fallback por si acaso no hay historial pero no es root
                router.replace({ name: 'home' });
            }
        }
    });
});
</script>
    <template>
    <v-app>
        <RouterView />
        <GlobalFeedback />
    </v-app>
    </template>
    <style>
    
    html, body, #app {
    height: 100%;
    user-select: none;
    -webkit-tap-highlight-color: transparent; 
    background-color: #0a0a0aff;
    overscroll-behavior: none;
    }
    .v-application {
    padding-top: calc(env(safe-area-inset-top) + 20px); 
    /* padding-bottom: env(safe-area-inset-bottom); */
    height: 100%; 
    display: flex;
    flex-direction: column;
    }
    .v-app-bar {
        padding-top: calc(env(safe-area-inset-top) + 25px);
        height: auto !important; /* Dejar que crezca lo necesario */
    }
    .v-app-bar .v-toolbar__content {
        height: 50px !important; /* Altura estándar MD3 */
    }
    /* Permitir selección en inputs */
    input, textarea {
    user-select: text;
    }
</style>