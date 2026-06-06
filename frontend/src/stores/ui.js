import { defineStore } from "pinia";
import { ref  } from "vue";

export const useUIStore = defineStore("ui", () => {
    // --- ESTADO --- (state)
    const isLoading = ref(false)
    const loadingMessage = ref('')
    const showLogoutConfirm = ref(false)
    // --- Respuesta del dialogo de confirmacion ---
    let logoutConfirmResolve = null
    // --- ACCIONES --- (actions)

    // inicia el dialogo de carga
    const startLoading = (message = 'Cargando ...') => {
        loadingMessage.value = message
        isLoading.value = true
    }
    // Detiene y oculta el dialogo
    const stopLoading = () => {
        isLoading.value = false
        loadingMessage.value = ''
    }
    // dialogo de confirmacion para cerrar sesion
    const confirmLogout = () => {
        showLogoutConfirm.value = true
        return new Promise((resolve) => {
            logoutConfirmResolve = resolve
        })
    }
    // resuelve la promesa y cierra el dialogo
    const resolveLogoutConfirm = (decision) => {
        if (logoutConfirmResolve) {
            logoutConfirmResolve(decision)
        }
        showLogoutConfirm.value = false
        logoutConfirmResolve = null
    }

    // --- NOTIFICACIONES ---
    const snackbar = ref({
        show: false,
        message: '',
        color: 'inverse-surface', // Color por defecto (negro suave en temas claros)
        timeout: 3000
    })

    const showSnackbar = (message, type = 'info') => {
        snackbar.value.message = message
        snackbar.value.show = true
        
        // Asignar colores según el tipo
        switch(type) {
            case 'success': snackbar.value.color = 'success'; break;
            case 'error': snackbar.value.color = 'error'; break;
            case 'warning': snackbar.value.color = 'warning'; break;
            default: snackbar.value.color = 'inverse-surface'; 
        }
    }

    return {
        isLoading,
        loadingMessage,
        showLogoutConfirm,
        startLoading,
        stopLoading,
        confirmLogout,
        resolveLogoutConfirm,
        snackbar,
        showSnackbar
    }
})