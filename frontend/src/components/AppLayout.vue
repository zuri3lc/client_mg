
<script setup>
import { watch, ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { syncData, downloadDataFromServer } from '@/services/sync';
import { useUIStore } from '@/stores/ui';

const uiStore = useUIStore();
const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const selectedTab = ref(route.name);

const isOnline = ref(navigator.onLine);

const onHomePage = computed(() => route.name === 'home');

const updateOnlineStatus = () => {
    isOnline.value = navigator.onLine;
};

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

const handleSync =  async () => {
    uiStore.loadingMessage = 'Forzando sincronización manual (Up&Download)...'
    console.log('Forzando sincronización manual (Up&Download)...');
    try{
        uiStore.startLoading('Sincronizando datos ...')
        await syncData();
    } catch (e) {
        console.error('Error al sincronizar datos:', e);
    } finally {
        uiStore.stopLoading();
    }
};

const handleDownload = async () => {
    uiStore.loadingMessage = 'Descargando datos del servidor (Download)...'
    console.log('Descargando datos del servidor (Download)...');
    try{
        uiStore.startLoading('Descargando datos del servidor ...')
        await downloadDataFromServer();
    } catch (e) {
        console.error('Error al descargar datos del servidor:', e);
    } finally {
        uiStore.stopLoading();
    }
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