<script setup>
import { watch, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const selectedTab = ref(route.name);

watch(() => route.name, (newRouteName) => {
    selectedTab.value = newRouteName;
}, { immediate: true});

const handleLogout = () => {
    authStore.logout();
    router.push({ name: 'login' });
};
</script>

<template>
    <v-layout>
    <v-app-bar color="background" elevation="0">
        <v-app-bar-title>Client Manager</v-app-bar-title>
        <v-spacer></v-spacer>
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
