<script setup>
import { watch, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { syncData } from '@/services/sync';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const selectedTab = ref(route.name);

watch(() => route.name, (newRouteName) => {
    selectedTab.value = newRouteName;
}, { immediate: true});

const handleLogout = async () => {
    await authStore.logout();
    router.push({ name: 'login' });
};
const handleSync = () => {
    console.log('Forzando sincronización manual...');
    syncData();
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
        
        <v-btn icon @click="handleSync">
        <v-icon size="small">mdi-sync</v-icon>
        </v-btn>

        <v-btn icon @click="handleLogout">
        <v-icon size="small">mdi-logout</v-icon>
        </v-btn>
    </v-app-bar>

    <v-main>
        <router-view />
    </v-main>

    <v-bottom-navigation 
    bgColor= "background"
    class="justify-center"
    mode="shift"
    v-model="selectedTab"  >

    <v-btn
    color="icons"
    variant="plain"
    value="home" 
    :to="{ name: 'home' }"
    >
    <v-icon
    size="large">mdi-account-group
    </v-icon>

    <span>Clientes</span>

    </v-btn>

    <v-btn
    color="icons"
    variant="plain"
    value="new-client"
    :to="{ name: 'new-client' }"
    >

    <v-icon 
    size="large">mdi-plus-circle
    </v-icon>

    <span>Nuevo</span>

    </v-btn>
</v-bottom-navigation>

    </v-layout>
</template>

<style>
.bar-title {
    font-size: 1.25rem !important; /* Mantiene el tamaño de fuente de un título de app-bar */
    font-weight: 500;
    text-transform: none; /* Evita que el texto esté en mayúsculas */
    letter-spacing: normal;
    color: inherit;
    padding-left: 16px !important;
}
</style>