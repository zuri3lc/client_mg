 <script setup>
// 1. 'computed' es nuevo, para el cálculo en tiempo real
import { onMounted, ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useClientStore } from '@/stores/client';
import { useMovimientoStore } from '@/stores/movimiento';

const route = useRoute();
const router = useRouter();
const clientStore = useClientStore();
const movimientoStore = useMovimientoStore();

// --- INICIO DE LA MODIFICACIÓN ---

// NUEVO: Observador (watch) para la reactividad del ID.
// Este bloque de código vigila el cliente que está seleccionado en el store.
watch(() => clientStore.selectedClient, (clienteActualizado) => {
    // Nos aseguramos de que haya un cliente cargado.
    if (clienteActualizado) {
        // Obtenemos el ID de la URL actual (que podría ser el ID temporal negativo).
        const idEnUrl = Number(route.params.id);

        // La condición clave: si el ID en la URL es diferente al ID del cliente
        // que ahora está en el store, significa que la sincronización ocurrió y el ID cambió.
        if (idEnUrl !== clienteActualizado.id) {
            console.log(`El ID del cliente cambió de ${idEnUrl} a ${clienteActualizado.id}. Redirigiendo...`);
            
            // Reemplazamos la URL actual con la nueva URL que contiene el ID permanente.
            // Usamos 'replace' para no crear un historial de navegación innecesario.
            router.replace({ name: 'client-detail', params: { id: clienteActualizado.id } });
        }
    }
}, {
    // 'deep: true' es importante para que el observador detecte cambios
    // dentro de las propiedades del objeto del cliente.
    deep: true 
});

const montoAbono = ref('');
const montoCredito = ref('');
const loadingSave = ref(false); // Para el nuevo botón de guardar

const saldoFinalCalculado = computed(() => {
    const saldoActual = parseFloat(clientStore.selectedClient?.saldo_actual) || 0;
    const abono = parseFloat(montoAbono.value) || 0;
    const Credito = parseFloat(montoCredito.value) || 0;
    
    return saldoActual - abono + Credito;
});

const handleSaveChanges = async () => {
    loadingSave.value = true;
    const abono = parseFloat(montoAbono.value) || 0;
    const Credito = parseFloat(montoCredito.value) || 0;

    try {
        if (abono > 0) {
            await movimientoStore.addMovimiento({
                tipo: 'abono',
                monto: -abono, // Los abonos siempre se guardan como negativos
                clientId: clientStore.selectedClient.id
            });
        }
        if (Credito > 0) {
            await movimientoStore.addMovimiento({
                tipo: 'Credito',
                monto: Credito, // Los Creditos siempre se guardan como positivos
                clientId: clientStore.selectedClient.id
            });
        }

        montoAbono.value = '';
        montoCredito.value = '';
        await clientStore.fetchClientById(clientStore.selectedClient.id);
        
    } catch (error) {
        console.error("Error al guardar cambios:", error);
        alert("No se pudieron guardar los movimientos.");
    } finally {
        loadingSave.value = false;
    }
};

onMounted(() => {
    const clientId = parseInt(route.params.id, 10);
    clientStore.fetchClientById(clientId);
    movimientoStore.loadMovimientosFromDB(clientId);
});

const getStatusColor = (status) => {
    switch (status) {
    case 'bueno':
        return 'success';
    case 'regular':
        return 'info';
    case 'moroso':
        return 'error';
    default:
        return 'grey';
    }
};

const formatCurrency = (amount) => {
    const numericAmount = parseFloat(amount); 
    if (isNaN(numericAmount)) { 
        return 'N/A'; 
    }
    return new Intl.NumberFormat('es-MX', { 
        style: 'decimal',
        minimumFractionDigits: 2,
    }).format(numericAmount);
};
</script>

<template>
    <v-layout>
        <v-app-bar density="compact" color="background" elevation="0">
        <!-- <v-btn icon @click="router.back()"><v-icon>mdi-arrow-left</v-icon></v-btn> -->
        <v-spacer></v-spacer>
        <v-btn
        v-if="clientStore.selectedClient"
        icon 
        :to="{ name: 'edit-client', params: { id: clientStore.selectedClient.id } }"
        >
        <v-icon>mdi-pencil</v-icon>
        </v-btn>
        </v-app-bar>
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
                    <v-list-item title="Detalles y Saldos"></v-list-item>
                    <v-divider class="mb-4"></v-divider>

                    <v-row no-gutters class="py-2 px-4 align-center">
                        <v-col cols="4" class="font-weight-medium text-subtitle-2 text-grey-darken-2">Saldo Actual</v-col>
                        <v-col cols="8" class="text-h6 font-weight-bold text-right text-info">
                            $ {{ formatCurrency(clientStore.selectedClient.saldo_actual) }}
                        </v-col>
                    </v-row>
                    <v-divider class="my-2"></v-divider>

                    <v-row no-gutters class="py-2 px-4 align-center">
                        <v-col cols="4" class="font-weight-medium text-subtitle-2 text-grey-darken-2">Saldo Final</v-col>
                        <v-col cols="8" class="text-h6 font-weight-bold text-right text-warning">
                            $ {{ formatCurrency(saldoFinalCalculado) }}
                        </v-col>
                    </v-row>
                    <v-divider class="my-2"></v-divider>

                    <v-row no-gutters class="py-2 px-4 align-center">
                        <v-col cols="4" class="font-weight-medium text-subtitle-2 text-grey-darken-2">Abono</v-col>
                        <v-col cols="8">
                            <v-text-field v-model.number="montoAbono" type="number" variant="underlined" density="compact" hide-details prefix="$"></v-text-field>
                        </v-col>
                    </v-row>
                    
                    <v-row no-gutters class="py-2 px-4 align-center">
                        <v-col cols="4" class="font-weight-medium text-subtitle-2 text-grey-darken-2">Credito</v-col>
                        <v-col cols="8">
                            <v-text-field v-model.number="montoCredito" type="number" variant="underlined" density="compact" hide-details prefix="$"></v-text-field>
                        </v-col>
                    </v-row>
                    <v-divider class="my-2"></v-divider>

                    <v-row no-gutters class="pt-4 pb-2 px-4 align-center">
                    <v-col cols="4" class="font-weight-medium text-subtitle-2 text-grey-darken-2">
                        Ubicacion
                    </v-col>
                    <v-col cols="8" class="text-subtitle-1 text-h7 font-weight-light text-right">
                        {{ clientStore.selectedClient.ubicacion_aproximada || 'No añadido' }}
                    </v-col>
                    </v-row>
                    <v-divider class="mb-4"></v-divider>

                    <v-row no-gutters class="py-2 px-4 align-center">
                    <v-col cols="4" class="font-weight-medium text-subtitle-2 text-grey-darken-2">
                        Comentario
                    </v-col>
                    <v-col cols="8" class="text-subtitle-1 text-h7 font-weight-light text-right">
                        {{ clientStore.selectedClient.comentario || 'No añadido' }}
                    </v-col>
                    </v-row>
                    <v-divider class="mb-4"></v-divider>

                    <v-row no-gutters class="py-2 px-4 align-center">
                        <v-col cols="4" class="font-weight-medium text-subtitle-2 text-grey-darken-2">Estado</v-col>
                        <v-col cols="8" class="d-flex justify-end">
                            <v-chip 
                            :color="getStatusColor(clientStore.selectedClient.estado_cliente)" 
                            size="small">{{ clientStore.selectedClient.estado_cliente }}
                            </v-chip>
                        </v-col>
                    </v-row>
                    <v-divider class="my-2"></v-divider>

                    <v-card-actions class="pa-4">
                        <v-spacer></v-spacer>
                        <v-btn color="primary" variant="flat" @click="handleSaveChanges" :loading="loadingSave" :disabled="!montoAbono && !montoCredito">
                            Guardar Movimiento
                        </v-btn>
                    </v-card-actions>

                </v-card>
                <v-card color="background" elevation="0">
                    <v-list-item title="Movimientos"></v-list-item>
                    <v-divider></v-divider>
                    <div v-if="movimientoStore.movimientos.length === 0" class="text-center pa-4">
                    <p class="text-caption">Este cliente no tiene movimientos.</p>
                    </div>

                    <v-list v-else bg-color="transparent">
                    <v-list-item
                    class="last-item"
                    v-for="movimiento in movimientoStore.movimientos"
                    :key="movimiento.id"
                    >
                    <v-list-item-title>{{ movimiento.tipo_movimiento.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) }}</v-list-item-title>
                    <v-list-item-subtitle>
                        <!-- {{ new Date(movimiento.fecha_movimiento).toLocaleDateString() }} -->
                        {{ new Date(movimiento.fecha_movimiento + 'T00:00:00').toLocaleDateString('es-MX') }}
                    </v-list-item-subtitle>
                    <template v-slot:append>
                    <span 
                    :class="[
                        'font-weight-bold', // La clase estática ahora es parte del array
                        movimiento.monto < 0 ? 'text-success' : 'text-warning' // La lógica de color correcta
                    ]"
                    >
                    {{ formatCurrency(movimiento.monto) }}
                    </span>
                    </template>
                </v-list-item>
                </v-list>
                <v-divider ></v-divider>
                </v-card>

                <v-row no-gutters class="py-2 px-4 align-center">
                    <v-col cols="4" class="font-weight-medium text-subtitle-2 text-grey-darken-2">Teléfono</v-col>
                    <v-col cols="8" class="text-subtitle-1 text-right">{{ clientStore.selectedClient.telefono || 'No especificado' }}</v-col>
                </v-row>
                <v-divider class="my-2"></v-divider>

            </v-container>
            <div v-else class="text-center mt-16">
                </div>
        </v-main>
    </v-layout>
</template>