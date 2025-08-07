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
    if (!nombre.value) {
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
// Regla de validación para el saldo
const saldoRules = [
    value => !!value || 'El saldo inicial es obligatorio.',
    value => (value && value > 0) || 'El saldo inicial debe ser mayor a cero.',
];

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
            label="Nombre"
            hint="(OBLIGATORIO)"
            variant="outlined"
            class="mb-4"
            required
        ></v-text-field>

        <v-text-field
            v-model.number="saldoInicial"
            hint="(OBLIGATORIO) El saldo debe ser mayor a cero"
            label="Saldo Inicial"
            type="number"
            prefix="$"
            variant="outlined"
            class="mb-4"
            :rules="saldoRules"
        ></v-text-field>

        <v-text-field
            v-model="telefono"
            label="Teléfono"
            hint="(OPCIONAL)"
            variant="outlined"
            class="mb-4"
        ></v-text-field>

        <v-text-field
            v-model="ubicacion"
            label="Ubicación aproximada"
            variant="outlined"
            class="mb-4"
        ></v-text-field>

        <v-text-field
            v-model="comentario"
            label="Comentario"
            variant="outlined"
            class="mb-4"
        ></v-text-field>

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