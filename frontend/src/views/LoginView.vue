<script setup>
import { ref } from 'vue';
import api from '@/services/api';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useClientStore } from '@/stores/client';
import { syncData } from '@/services/sync';
import { useUIStore } from '@/stores/ui';

const uiStore = useUIStore();
const router = useRouter(); // instancia del router a redirigir
const authStore = useAuthStore(); //instancia del store
const clientStore = useClientStore(); //instancia del store

// 1. Variables relativas para almacenar los datos del formulario
const username = ref('');
const password = ref('');
const loading = ref(false); //muestra un estado de carga en el boton 
const errorMessage = ref(null);
const syncMessage = ref(null);

// 2. Funcion que se ejecuta al hacer clic al boton
const handleLogin = async() => {
    // loading.value = true;
    errorMessage.value = null;
    syncMessage.value = '';

    try {
        uiStore.startLoading('Iniciando Sesión...')
        await authStore.login({
            username: username.value,
            password: password.value
        });

        uiStore.loadingMessage = 'Sincronizando clientes y movimientos: Remoto => Local...'
        syncMessage.value = 'Sincronizando clientes y movimientos: Remoto => Local...';
        await clientStore.initialSync();

        //redireccion
        router.push({name: 'home'});
    } catch (error){
        // manejo de errores
        console.error('Login Fallido:', error);
        if (error.response && error.response.status === 401) {
            errorMessage.value = 'Credenciales Incorrectas';
        } else {
            errorMessage.value = 'Error de Servidor'
        }
    } finally {
        // sin importar la respuesta detenemos la carga
        // loading.value = false;
        uiStore.stopLoading();
    }
};

const handleSync = () => {
    console.log('Forzando sincronización manual...');
    syncData();
};
</script>

<template>
    
    <v-container class="fill-height">
        <v-responsive class="d-flex align-center text-center fill-height">

            <div class="mx-auto" style="max-width: 380px;">
                <h1 class="text-h4 font-weight-bold mb-15">
                    Gestor de Clientes
                </h1>

                <v-alert
                v-if="errorMessage"
                type="error"
                density="compact"
                class="mb-3 text-center"
                rounded="lg"
                variant="tonal"
                >
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
                v-model="password"
                hint="Cuidado con los espacios y las mayusculas"
                label="Contraseña"
                type="password"
                variant="underlined"
                rounded="lg"
                ></v-text-field>

                <div class="d-flex flex-column align-center">
                    <v-btn
                    :loading="loading"
                    @click="handleLogin"
                    color="primary"
                    rounded="pill"
                    class="mt-5"
                    >
                        Log in
                    </v-btn>

                    <v-btn
                    :to="{ name: 'register' }"
                    variant="plain"
                    rounded="pill"
                    size="x-small"
                    class="mt-5"
                    >
                        REGISTRO NUEVO
                    </v-btn>
                </div>
                
            </div>
            
        </v-responsive>
        
    </v-container>

</template>

<style scoped>
.loginContainer{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    /* mas estilos */
}
</style>