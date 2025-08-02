// src/stores/movimiento.js
import { defineStore } from 'pinia';
import { db } from '@/services/db';
import { ref } from 'vue';
import { useAuthStore } from './auth';


export const useMovimientoStore = defineStore('movimiento', () => {
    const movimientos = ref([]);

    const loadMovimientosFromDB = async (clientId) => {
    try {
        
        const localMovimientos = await db.movimientos
            .where('cliente_id').equals(clientId)
            .toArray();

        localMovimientos.sort((a, b) => {
            const dateA = new Date(a.fecha_movimiento);
            const dateB = new Date(b.fecha_movimiento);
            
            if (dateB - dateA !== 0) {
                return dateB - dateA;
            }
            
            return b.id - a.id;
        });

        movimientos.value = localMovimientos;
    } catch(error) {
        console.error('Error al cargar movimientos locales:', error);
        movimientos.value = [];
    }
};

    const addMovimiento = async (movimientoData) => {
        const authStore = useAuthStore();
        try {
            await db.transaction('rw', db.clients, db.movimientos, async () => {
                const client = await db.clients.get(movimientoData.clientId);
                if (!client) throw new Error('Cliente no encontrado');

                const saldoAnterior = client.saldo_actual || 0.00;
                const nuevoSaldo = parseFloat(saldoAnterior) + parseFloat(movimientoData.monto);

                const newMovimiento = {
                    id: -Date.now(), // ID temporal
                    cliente_id: movimientoData.clientId,
                    fecha_movimiento: new Date().toISOString().split('T')[0],
                    tipo_movimiento: movimientoData.tipo,
                    monto: movimientoData.monto,
                    saldo_anterior: saldoAnterior,
                    saldo_final: nuevoSaldo,
                    usuario_sistema_id: authStore.user.id,
                    needsSync: 1 // Marcar para sincronizar
                };

                await db.movimientos.add(newMovimiento);

                await db.clients.update(movimientoData.clientId, {
                    saldo_actual: nuevoSaldo
                });
                movimientos.value.unshift(newMovimiento);
                console.log('Movimiento guardado y saldo actualizado localmente')
            })
        } catch (error) {
            console.error('Error al guardar movimiento y actualizar saldo:', error);
            throw error;
        }
    }

    return { movimientos, loadMovimientosFromDB, addMovimiento  };
});