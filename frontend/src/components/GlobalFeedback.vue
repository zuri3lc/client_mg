<script setup>
import { useUIStore } from '@/stores/ui';
const uiStore = useUIStore()
</script>

<template>
    <v-dialog v-model="uiStore.isLoading" persistent width="auto">
    <v-card color="background" elevation="0">
        <v-card-text class="d-flex align-center pa-5">
        <v-progress-circular indeterminate color="primary" class="mr-4"></v-progress-circular>
        <span>{{ uiStore.loadingMessage }}</span>
        </v-card-text>
    </v-card>
    </v-dialog>

    <v-dialog v-model="uiStore.showLogoutConfirm" persistent max-width="400px">
    <v-card color="background" elevation="0">
        <v-card-title class="text-h5">Cerrar Sesión</v-card-title>
        <v-card-text>
        Hay datos locales pendientes de sincronizar. Sincroniza antes de cerrar la sesion.
        <br><br>
        <strong>¿Estás seguro de que quieres continuar?</strong>
        </v-card-text>
        <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn variant="text" @click="uiStore.resolveLogoutConfirm(false)">
            Cancelar
        </v-btn>
        <v-btn color="error" variant="flat" @click="uiStore.resolveLogoutConfirm(true)">
            Cerrar Sesión
        </v-btn>
        </v-card-actions>
    </v-card>
    </v-dialog>

    <!-- Notificaciones Globales (Snackbar) -->
    <v-snackbar
        v-model="uiStore.snackbar.show"
        :color="uiStore.snackbar.color"
        :timeout="uiStore.snackbar.timeout"
        location="bottom"
        elevation="2"
    >
        {{ uiStore.snackbar.message }}

        <template v-slot:actions>
            <v-btn
                variant="text"
                icon="mdi-close"
                @click="uiStore.snackbar.show = false"
            ></v-btn>
        </template>
    </v-snackbar>
    
</template>