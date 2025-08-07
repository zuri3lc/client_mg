<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useClientStore } from '@/stores/client';

const route = useRoute();
const router = useRouter();
const clientStore = useClientStore();

const nombre = ref('');
const telefono = ref('');
const ubicacion = ref('');
const comentario = ref('');
const estado = ref('regular'); // selector de estado
const loading = ref(false);

const deleteDialog = ref(false);
const deleting = ref(false);

const handleDeleteClient = async () => {
    deleting.value = true;
    try {
        await clientStore.markClientForDeletion(clientStore.selectedClient.id);
        deleteDialog.value = false;
        // Navegamos dos pasos atrás para volver a la (HomeView)
        router.go(-2); 
    } catch (error) {
        console.error("Error al eliminar:", error);
        alert("No se pudo eliminar el cliente.");
    } finally {
        deleting.value = false;
    }
};

onMounted(async() => {
    const clientId = parseInt(route.params.id, 10);
    await clientStore.fetchClientById(clientId);

    const cliente = clientStore.selectedClient;
    if (cliente){
        nombre.value = cliente.nombre;
        telefono.value = cliente.telefono || "";
        ubicacion.value = cliente.ubicacion_aproximada || "";
        comentario.value = cliente.comentario || "";
        estado.value = cliente.estado_cliente;
    }
});

const handleUpdateClient = async () => {
    loading.value = true;
    try {
        await clientStore.updateClient(clientStore.selectedClient.id, {
            nombre: nombre.value,
            telefono: telefono.value,
            ubicacion: ubicacion.value,
            comentario: comentario.value,
            estado: estado.value,
        });
        router.back();
    } catch (error) {
        console.error("Error al actualizar:", error);
        alert("No se pudieron guardar los cambios.");
    } finally {
        loading.value = false;
    }
};

</script>

<template>
    <v-layout>
    <v-app-bar class="text-end pr-4" density="compact" color="background" elevation="0">
        <v-btn icon @click="router.back()"><v-icon>mdi-arrow-left</v-icon></v-btn>
        <v-app-bar-title>Editar Cliente</v-app-bar-title>
    </v-app-bar>

    <v-main>
        <v-container v-if="clientStore.selectedClient">
        <v-form @submit.prevent="handleUpdateClient">
            <v-text-field v-model="nombre" label="Nombre completo" variant="underlined" class="mb-4" required></v-text-field>
            <v-text-field v-model="telefono" label="Teléfono" variant="underlined" class="mb-4"></v-text-field>
            <v-text-field v-model="ubicacion" label="Ubicación" variant="underlined" class="mb-4"></v-text-field>
            <v-text-field v-model="comentario" label="Comentario" variant="underlined" class="mb-4"></v-text-field>

            <v-select
            v-model="estado"
            :items="['regular', 'bueno', 'moroso']"
            label="Estado del cliente"
            variant="underlined"
            class="mb-4"
            ></v-select>
            

            <v-btn :loading="loading" type="submit" color="primary" block size="large" variant="outlined">
            Guardar Cambios
            </v-btn>
        </v-form>

        <v-btn 
            @click="deleteDialog = true" 
            color="error" 
            variant="outlined" 
            block 
            class="mt-4"
            >
                Eliminar Cliente
            </v-btn>

        </v-container>
    </v-main>

    <v-dialog v-model="deleteDialog" persistent max-width="400px">
            <v-card color="background" elevation="0">
                <v-card-title class="text-h5">Confirmar Eliminación</v-card-title>
                <v-card-text>
                    ¿Estás seguro de que quieres eliminar a 
                    <strong>{{ clientStore.selectedClient?.nombre }}</strong>? 
                    Esta acción no se puede deshacer.
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn variant="text" @click="deleteDialog = false">Cancelar</v-btn>
                    <v-btn 
                        color="error" 
                        variant="flat" 
                        @click="handleDeleteClient"
                        :loading="deleting"
                    >
                        Eliminar
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

    </v-layout>
</template>