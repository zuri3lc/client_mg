import { NativeBiometric } from '@capgo/capacitor-native-biometric';

const SERVER_NAME = 'gestion_clientes_app'; // Identificador para el llavero/keystore

export default {
    /**
     * Verifica si el hardware biométrico está disponible.
     * @returns {Promise<boolean>} true si hay biometría disponible.
     */
        async checkBiometry() {
        try {
            const result = await NativeBiometric.isAvailable();
            return result.isAvailable;
        } catch (error) {
            console.warn('Biometría no disponible:', error);
            return false;
        }
    },

    /**
     * Guarda las credenciales de forma segura tras un login exitoso.
     * @param {string} username 
     * @param {string} password 
     */
    async saveCredentials(username, password) {
        try {
        // Necesitamos verificar disponibilidad primero para evitar errores
        const isAvailable = await this.checkBiometry();
        if (!isAvailable) return;

        await NativeBiometric.setCredentials({
            username,
            password,
            server: SERVER_NAME,
        });
        console.log('Credenciales biométricas guardadas correctamente.');
        } catch (error) {
        console.error('Error guardando credenciales biométricas:', error);
        }
    },

    /**
     * Intenta recuperar las credenciales. Esto mostrará el prompt biométrico al usuario.
     * @returns {Promise<{username: string, password: string} | null>} Credenciales o null si falla/cancela.
     */
    async getCredentials() {
    try {
        // 1. Forzamos la verificación de identidad explícitamente
        // Esto asegura que SIEMPRE aparezca el prompt de huella/cara
        await NativeBiometric.verifyIdentity({
            reason: "Autentícate para iniciar sesión",
            title: "Inicio de Sesión Biométrico",
            subtitle: "Usa tu huella o rostro",
            description: "Es necesario verificar tu identidad para acceder a las credenciales guardadas"
        });

        // 2. Si la verificación pasa, recuperamos las credenciales
        const credentials = await NativeBiometric.getCredentials({
            server: SERVER_NAME,
        });
        return {
            username: credentials.username,
            password: credentials.password,
        };
        } catch (error) {
        console.log('Autenticación biométrica fallida o cancelada:', error.message);
        return null;
        }
    },

    /**
     * Elimina las credenciales guardadas (ej. al cerrar sesión si se requiere, o limpiar datos).
     */
    async deleteCredentials() {
        try {
        await NativeBiometric.deleteCredentials({
            server: SERVER_NAME,
        });
        console.log('Credenciales biométricas eliminadas.');
        } catch (error) {
        console.warn('No se pudieron eliminar las credenciales:', error);
        }
    }
    };
