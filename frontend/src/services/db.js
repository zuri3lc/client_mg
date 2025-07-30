import Dexie from "dexie";

// 1. crear instancia db
export const db = new Dexie("ClientManagementDB");

//Esquema de la DB
db.version(1).stores({
    /**TABLA CLIENTES */
    clients: 'id, [nombre+usuario_sistema_id], usuario_sistema_id, telefono, needsSync',
    /**TABLA MOVIMIENTOS */
    movimientos: 'id, cliente_id, usuario_sistema_id, fecha_movimiento, needsSync',
});


// TODO
/* 
 * extender las clases de Dexie para añadir métodos útiles.
 * Por ejemplo, un método para marcar un cliente como "necesita sincronización".
 * ¡Esto es opcional pero muy potente! Por ahora lo dejamos así de simple.
 */

// db.clients.mapToClass(Client);
// db.movimientos.mapToClass(Movimiento);