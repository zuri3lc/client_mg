<script setup>
import { ref } from 'vue';
import api from '@/services/api';
import { useRouter } from 'vue-router';

const router = useRouter();

const username = ref('');
const password = ref('');
const passwordConfirm = ref('');
const nombre = ref('');
const masterKey = ref('');
const loading = ref(false);
const errorMessage = ref(null);

const handleRegister = async () => {
    if (password.value !== passwordConfirm.value) {
        errorMessage.value = 'Las contraseñas no coinciden';
        return;
    }

    if (!username.value || !password.value || !masterKey.value) {
        errorMessage.value = 'Usuario, Contraseña y MasterKey son obligatorios';
        return;
    }

    loading.value = true;
    errorMessage.value = null;

    try{
        const userData = {
            username: username.value,
            password: password.value,
            nombre: nombre.value || null,
            master_key: masterKey.value,
        };

        await api.register(userData);

        alert('Registro exitoso, puede iniciar sesion');
        router.push({ name: 'login'});

        } catch (error){
            console.error('Registro Fallido:', error);
            if (error.response) {
                errorMessage.value = error.response.data.message;
            } else {
                errorMessage.value = 'No se pudo completar el registro';
            }
        } finally {
            loading.value = false;
        }
    };
</script>

<template>
<v-container class="fill-height" fluid>
    <v-responsive class="d-flex align-center text-center fill-height">
        <div class="mx-auto" style="max-width: 380px;">
        <h1 class="text-h4 font-weight-bold mb-15">
            Crear Nuevo Usuario
        </h1>

        <v-alert
        v-if="errorMessage"
        type="error"
        variant="tonal"
        rounded="lg"
        class="mb-4 text-left"
        dense>
            {{ errorMessage }}
        </v-alert>

        <v-text-field
        v-model="username"
        label="Nombre de Usuario"
        variant="underlined"
        rounded="lg"
        class="mb-2"
        ></v-text-field>

        <v-text-field
        v-model="nombre"
        label="Nombre Completo (opcional)"
        rounded="lg"
        variant="underlined"
        class="mb-2"
        ></v-text-field>

        <v-text-field
        v-model="password"
        label="Contraseña"
        hint="Cuidado con los espacios y las mayusculas"
        type="password"
        variant="underlined"
        rounded="lg"
        class="mb-2"
        ></v-text-field>

        <v-text-field
        v-model="passwordConfirm"
        label="Confirmar Contraseña"
        hint="Cuidado con los espacios y las mayusculas"
        type="passwordConfirm"
        variant="underlined"
        rounded="lg"
        class="mb-2"
        ></v-text-field>

        <v-text-field 
        v-model="masterKey" 
        label="Llave Maestra" 
        type="password" 
        variant="underlined"
        rounded="lg"
        ></v-text-field>

        <div class="d-flex flex-column align-center">
            <v-btn
            :loading="loading"
            @click="handleRegister"
            color="primary"
            rounded="pill"
            class="mt-5">
                Crear Usuario
            </v-btn>

            <v-btn
            :to="{ name: 'login' }"
            variant="plain"
            rounded="pill"
            size="x-small"
            class="mt-5">
                Volver a Inicio de Sesión
            </v-btn>
        </div>

    </div>
</v-responsive>
</v-container>
</template>