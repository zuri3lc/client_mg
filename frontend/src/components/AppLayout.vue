
<script setup>
import { watch, ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { syncData, downloadDataFromServer } from '@/services/sync';
import { useUIStore } from '@/stores/ui';
import { useClientStore } from '@/stores/client';
import { storeToRefs } from 'pinia';

const uiStore = useUIStore();
const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const clientStore = useClientStore();
const { searchQuery } = storeToRefs(clientStore);
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
    <v-app-bar density="compact" color="background" elevation="0" >
        <v-btn
        v-if="!onHomePage"
        :to="{name: 'home'}"
        variant="plain"
        rounded="lg"
        class="bar-title"
        >
            Client Manager
        </v-btn>
        
        <v-text-field
            v-else
            v-model="searchQuery"
            placeholder="Buscar..."
            prepend-inner-icon="mdi-magnify"
            variant="solo"
            density="compact"
            hide-details
            rounded="xl"
            class="ml-2 flex-grow-1"
            bg-color="surface-light"
            flat
            clearable
        ></v-text-field>
        <v-spacer v-if="!onHomePage"></v-spacer>
<!--  -->
        <v-btn v-if="onHomePage" icon @click="handleDownload" :disabled="!isOnline">
            <v-icon size="small">mdi-cloud-download-outline</v-icon>
            <v-tooltip activator="parent" location="bottom">{{ isOnline ? 'Descargar Datos' : 'Necesitas conexión' }}</v-tooltip>
        </v-btn>
        
        <!-- <v-btn v-if="onHomePage" icon @click="handleSync" :disabled="!isOnline">
            <v-icon size="small">mdi-sync</v-icon>
            <v-tooltip activator="parent" location="bottom">{{ isOnline ? 'Sincronizar' : 'Necesitas conexión' }}</v-tooltip>
        </v-btn> -->

        <v-btn icon @click="handleLogout">
        <v-icon size="small">mdi-logout</v-icon>
        <v-tooltip activator="parent" location="bottom">{{'Cerrar Sesion'}}</v-tooltip>
        </v-btn>
    </v-app-bar>

    <v-main>
        <div class="fill-height d-flex flex-column" style="overflow-y: auto;">
        <router-view />
        </div>
    </v-main>

    <v-bottom-navigation 
        app
        grow
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
.v-bottom-navigation {
    padding-bottom: env(safe-area-inset-bottom);
    height: calc(80px + env(safe-area-inset-bottom)) !important;
}

</style>