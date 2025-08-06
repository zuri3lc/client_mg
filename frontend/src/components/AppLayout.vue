
<script setup>
// PASO 1: Importamos las herramientas necesarias de Vue.
// - computed: para crear una variable que reacciona a los cambios (como la ruta).
// - onMounted/onUnmounted: para gestionar los eventos de conexión a internet.
import { watch, ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { syncData, downloadDataFromServer } from '@/services/sync';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const selectedTab = ref(route.name);

// PASO 2: Creamos una variable reactiva para saber si hay conexión.
// navigator.onLine nos da el estado actual del navegador.
const isOnline = ref(navigator.onLine);

// PASO 3: Creamos la propiedad computada que controla la visibilidad.
// Esta variable será 'true' SOLO si el nombre de la ruta actual es 'home'.
// En cualquier otra pantalla, será 'false'.
const onHomePage = computed(() => route.name === 'home');

// Función que se activa cuando el navegador detecta un cambio en la conexión.
const updateOnlineStatus = () => {
    isOnline.value = navigator.onLine;
};

// PASO 4: Activamos y desactivamos los "escuchas" de eventos.
// Esto es una buena práctica para que la app sea eficiente.
onMounted(() => {
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
});

onUnmounted(() => {
    window.removeEventListener('online', updateOnlineStatus);
    window.removeEventListener('offline', updateOnlineStatus);
});


watch(() => route.name, (newRouteName) => {
    selectedTab.value = newRouteName;
}, { immediate: true});

const handleLogout = async () => {
    await authStore.logout();
    router.push({ name: 'login' });
};
const handleSync = () => {
    console.log('Forzando sincronización manual (SUBE Y BAJA)...');
    syncData();
};
const handleDownload = () => {
    console.log('Descargando datos del servidor (SOLO BAJA)...');
    downloadDataFromServer();
};
</script>

<template>
    <v-layout>
    <v-app-bar density="compact" color="background" elevation="0">
        <v-btn
        :to="{name: 'home'}"
        variant="plain"
        rounded="lg"
        class="bar-title"
        >
            Client Manager
        </v-btn>
        <v-spacer></v-spacer>
<!--  -->
        <v-btn v-if="onHomePage" icon @click="handleDownload" :disabled="!isOnline">
            <v-icon size="small">mdi-cloud-download-outline</v-icon>
            <v-tooltip activator="parent" location="bottom">{{ isOnline ? 'Descargar Datos' : 'Necesitas conexión' }}</v-tooltip>
        </v-btn>
        
        <v-btn v-if="onHomePage" icon @click="handleSync" :disabled="!isOnline">
            <v-icon size="small">mdi-sync</v-icon>
            <v-tooltip activator="parent" location="bottom">{{ isOnline ? 'Sincronizar' : 'Necesitas conexión' }}</v-tooltip>
        </v-btn>

        <v-btn icon @click="handleLogout">
        <v-icon size="small">mdi-logout</v-icon>
        <v-tooltip activator="parent" location="bottom">{{'Cerrar Sesion'}}</v-tooltip>
        </v-btn>
    </v-app-bar>

    <v-main>
        <router-view />
    </v-main>

    <v-bottom-navigation 
        bgColor= "background"
        class="justify-center"
        mode="shift"
        v-model="selectedTab"
    >
        <v-btn
            color="icons"
            variant="plain"
            value="home" 
            :to="{ name: 'home' }"
        >
            <v-icon size="large">mdi-account-group</v-icon>
            <span>Clientes</span>
        </v-btn>

        <v-btn
            color="icons"
            variant="plain"
            value="new-client"
            :to="{ name: 'new-client' }"
        >
            <v-icon size="large">mdi-plus-circle</v-icon>
            <span>Nuevo</span>
        </v-btn>
    </v-bottom-navigation>
    </v-layout>
</template>

<style>
.bar-title {
    font-size: 1.25rem !important;
    font-weight: 500;
    text-transform: none;
    letter-spacing: normal;
    color: inherit;
    padding-left: 16px !important;
}
</style>