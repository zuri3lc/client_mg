<script setup>
import { onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useClientStore } from '@/stores/client';

const route = useRoute();
const router = useRouter();
const clientStore = useClientStore();

onMounted(() => {
    // 1. Obtenemos el ID de la URL
    const clientId = parseInt(route.params.id, 10);
    // 2. Le pedimos al store que busque y cargue los datos de ese cliente
    clientStore.fetchClientById(clientId);
});

const getStatusColor = (status) => {
    switch (status) {
    case 'bueno':
      return 'info'; // Verde
    case 'regular':
      return 'success';    // Azul
    case 'moroso':
      return 'error';   // Rojo
    default:
      return 'grey';    // Un color por defecto si el estado es inesperado
    }
};

</script>

<template>
    <v-layout>

    <v-main>
        <v-container v-if="clientStore.selectedClient">

        <div class="d-flex flex-column align-center my-4">
            <v-avatar color="primary" size="80" class="mb-2">
            <v-icon size="50" color="white">mdi-account</v-icon>
            </v-avatar>
            <div class="text-h5 font-weight-bold">{{ clientStore.selectedClient.nombre }}</div>
            <div class="text-caption">ID: {{ clientStore.selectedClient.id }}</div>
        </div>

        <v-card color="background" class="mb-4" elevation="0">

            <v-list-item title="Detalles del cliente"></v-list-item>

            <v-divider></v-divider>

            <v-row no-gutters class="py-2 px-4 align-center">
                        <v-col cols="4" class="font-weight-medium text-subtitle-2 text-grey-darken-2">
                            Nombre
                        </v-col>
                        <v-col cols="8" class="text-subtitle-1">
                            {{ clientStore.selectedClient.nombre }}
                        </v-col>
            </v-row>

            <v-row no-gutters class="py-2 px-4 align-center">
                        <v-col cols="4" class="font-weight-medium text-subtitle-2 text-grey-darken-2">
                            Teléfono
                        </v-col>
                        <v-col cols="8" class="text-subtitle-1">
                            {{ clientStore.selectedClient.telefono || 'No especificado' }}
                        </v-col>
            </v-row>

            <v-row no-gutters class="py-2 px-4 align-center">
                        <v-col cols="4" class="font-weight-medium text-subtitle-2 text-grey-darken-2">
                            Ubicación
                        </v-col>
                        <v-col cols="8" class="text-subtitle-1">
                            {{ clientStore.selectedClient.ubicacion_aproximada || 'No especificado' }}
                        </v-col>
            </v-row>

            <v-row no-gutters class="py-2 px-4 align-center">
                        <v-col cols="4" class="font-weight-medium text-subtitle-2 text-grey-darken-2">
                            Comentario
                        </v-col>
                        <v-col cols="8" class="text-subtitle-1">
                            {{ clientStore.selectedClient.comentario || 'Sin comentarios' }}
                        </v-col>
            </v-row>

            <v-row no-gutters class="py-2 px-4 align-center">
                        <v-col cols="4" class="font-weight-medium text-subtitle-2 text-grey-darken-2">
                            Creado
                        </v-col>
                        <v-col cols="8" class="text-subtitle-1">
                            {{ clientStore.selectedClient.fecha_adquisicion || 'No especificada' }}
                        </v-col>
            </v-row>

        </v-card>

        <v-card color="background" elevation="0">
            <v-list-item title="Movimientos"></v-list-item>
            <v-divider></v-divider>
            <v-card-text class="text-center mt-4">
            El historial de movimientos aparecerá aquí.
            </v-card-text>
        </v-card>

        </v-container>
        <div v-else class="text-center mt-16">
        <p>Cargando datos del cliente...</p>
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </div>

        <v-btn
        fab
        color="primary"
        class="app-fab"
        rounded="lg"
        size="large"
        >
        <v-icon>mdi-plus</v-icon>
        </v-btn>
    </v-main>
    </v-layout>
</template>

<style scoped>
.app-fab {
    position: fixed;
    right: 20px; /* Ajusta la distancia desde la derecha */
    bottom: 70px; /* Altura de la bottom-navigation (56px) + un margen (14px) = 70px */
    z-index: 1000; /* Asegura que esté por encima de todo, incluyendo la bottom-navigation (z-index 100 por defecto) */
    /* Para que sea cuadrado si size="large" no lo hace por sí solo */
    width: 50px; /* tamaño de un fab "large" */
    height: 50px;
    min-width: 50px; /* evita que se haga más pequeño */
}
</style>
