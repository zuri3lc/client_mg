<script setup>
import {ref, computed, onMounted} from 'vue';
import { useClientStore } from '@/stores/client';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';

const clientStore = useClientStore();
const authStore = useAuthStore();
const router = useRouter();
const username = authStore.user?.username || 'usuario';
// const searchQuery = ref('');
const { clients, searchQuery } = storeToRefs(clientStore);

onMounted(()=> {
    clientStore.loadClients();
});

const filteredClients = computed(() => {
    if (!searchQuery.value) {
        // return clientStore.clients;
        return clients.value;
    }
    return clientStore.clients.filter(client =>
        client.nombre.toLowerCase().includes(searchQuery.value.toLowerCase())
    );
});

const formatCurrency = (amount) => {
    const numericAmount = parseFloat(amount); 
    if (isNaN(numericAmount)) { 
        return 'N/A'; 
    }
    return new Intl.NumberFormat('es-MX', { 
        style: 'decimal', //
        minimumFractionDigits: 2,
    }).format(numericAmount);
};

const goToNewClient = () => {
    router.push({ name: 'new-client' });
};

const handleLogout = () => {
    authStore.logout();
    router.push({ name: 'login' });
};

const getStatusColor = (status) => {
    switch (status) {
    case 'bueno':
      return 'success'; // Verde
    case 'regular':
      return 'info';    // Azul
    case 'moroso':
      return 'error';   // Rojo
    default:
      return 'grey';    // Un color por defecto si el estado es inesperado
    }
};
</script>

<template>
    <v-container>
        <v-text-field
        v-model="searchQuery"
        label="Buscar clientes..."
        prepend-inner-icon="mdi-magnify"
        variant="solo"
        rounded="pill"
        density="compact"
        hide-details
        single-line
        class="mb-4"
        clearable
        clear-icon="mdi-close-circle"
        >
        </v-text-field>

        <div v-if="clientStore.clients.length === 0" class="text-center mt-16 ">
            <p>No hay clientes para mostrar.</p>
        </div>

        <v-list
        lines="two"
        v-else
        bg-color="transparent"
        
        >
            <v-list-item
            v-for="client in filteredClients"
            :key="client.id"
            :title="client.nombre"
            :subtitle="`${client.ubicacion_aproximada || 'N/A'}`"
            class="client-list-item mt-2"

            rounded="xl"

            :to="{ name: 'client-detail', params: {id: client.id} }"
            link
            >
            <div class="text-caption text-grey mt-1" v-if="client.comentario">
            {{ client.comentario }}
            </div>
            <template v-slot:prepend>
                <v-avatar color="primary">
                <v-icon color="white">mdi-account-cash-outline</v-icon>
                </v-avatar>
            </template>

            <template v-slot:append>
                <div class="d-flex flex-column align-end"> 
                    <div
                    class="d-flex justify-space-between flex-grow-1"
                    style="min-width: 125px">
                    <span class="">Saldo: $ </span>
                    <span class=" ml-2">{{formatCurrency(client.saldo_actual)}}</span>
                </div>
                <v-chip 
                    :color="getStatusColor(client.estado_cliente)"
                    size="x-small"
                    class="mt-1">
                    {{ client.estado_cliente }}
                </v-chip>
                </div>
            </template>

            </v-list-item>
        </v-list>
    </v-container>
</template>

<style scoped>
.client-list-item {
    border-bottom: 1px solid #212121;
    /* padding-bottom: 8px; */ 
}
.client-list-item:last-child {
    border-bottom: none;
}
</style>