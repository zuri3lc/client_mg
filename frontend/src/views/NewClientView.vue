<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useClientStore } from '@/stores/client';

const router = useRouter();

// Variables para los campos del formulario
const nombre = ref('');
const telefono = ref('');
const ubicacion = ref('');
const comentario = ref('');
const saldoInicial = ref(0.00);

const clientStore = useClientStore();

const loading = ref(false);

const handleSaveClient = async () => {
    if (!nombre.value || !saldoInicial.value) {
        alert('Nombre y saldo son obligatorios');
        return;
    }
    loading.value = true;
    try{
        await clientStore.addClient({
        nombre: nombre.value,
        telefono: telefono.value,
        ubicacion: ubicacion.value,
        comentario: comentario.value,
        saldo_inicial: saldoInicial.value,
        });
    router.back();
    } catch (error) {
        console.error('No se pudo guardar el cliente: ', error);
    } finally {
        loading.value = false;
    }
};
</script>

<template>
<v-layout style="max-width: 970px;">
    <v-app-bar color="background" elevation="0">
    <v-app-bar-title align="center">Nuevo Cliente</v-app-bar-title>
    </v-app-bar>

    <v-main>
    <v-container>
        <v-form @submit.prevent="handleSaveClient">
        <v-text-field
            v-model="nombre"
            label="Nombre completo"
            variant="outlined"
            class="mb-4"
            required
        ></v-text-field>

        <v-text-field
            v-model.number="saldoInicial"
            label="Saldo Inicial"
            type="number"
            step="0.01"
            prefix="$"
            variant="outlined"
            class="mb-4"
            required
        ></v-text-field>

        <v-text-field
            v-model="telefono"
            label="Teléfono"
            variant="outlined"
            class="mb-4"
        ></v-text-field>

        <v-text-field
            v-model="ubicacion"
            label="Ubicación aproximada"
            variant="outlined"
            class="mb-4"
        ></v-text-field>

        <v-textarea
            v-model="comentario"
            label="Comentario"
            variant="outlined"
            class="mb-4"
        ></v-textarea>

        <div class="d-flex flex-column align-center">
            <v-btn
                :loading="loading"
                type="submit"
                color="primary"
                size="large"
                rounded="pill"
                class="mb-5"
                >
                Guardar Cliente
            </v-btn>
        </div>
        </v-form>
    </v-container>
    </v-main>
</v-layout>
</template>