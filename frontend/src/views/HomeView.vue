<script setup>
// 1. Importamos lo que necesitamos
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

// 2. Creamos las instancias del store y el router
const authStore = useAuthStore();
const router = useRouter();

// 3. Obtenemos el nombre de usuario del store para personalizar el saludo
const username = authStore.user?.username || 'usuario';

// 4. Creamos la función para manejar el logout
const handleLogout = () => {
  // Llamamos a la acción de logout que ya existe en nuestro store
    authStore.logout();
  // Redirigimos al usuario a la página de login
    router.push({ name: 'login' });
};
</script>

<template>
<v-container class="fill-height d-flex justify-center align-center">
    <div class="text-center">
        <h1 class="text-h4 mb-4">¡Bienvenido, {{ username }}!</h1>
        <p class="mb-8">Has iniciado sesión correctamente.</p>

    <v-btn 
        color="primary" 
        @click="handleLogout"
        >
            Cerrar Sesión
        </v-btn>
    </div>
</v-container>
</template>

<style scoped>
/* Puedes añadir estilos aquí si lo deseas */
</style>