// Importaciones de Estilos
import '@mdi/font/css/materialdesignicons.css';
import 'vuetify/styles'

// Importaciones de Vuetify
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

// Configuración del Tema Oscuro (¡justo como en tus diseños!)
const c_mDarkTheme = {
dark: true,
colors: {
    background: '#121212', // Fondo principal oscuro
    surface: '#212121',    // Color para tarjetas y superficies, un gris ligeramente más claro
    primary: '#4DB6AC',   // Un tono de aguamarina/teal sutil, no muy brillante
    secondary: '#B0BEC5',  // Un gris azulado para elementos secundarios
    icons: '#FFFFFF',
    error: '#EF5350',      // Un rojo suave para errores y saldos negativos
    info: '#2196F3',
    success: '#4CAF50',
    warning: '#FB8C00',}
}

export const vuetify = createVuetify({
components,
directives,
theme: {
    defaultTheme: 'c_mDarkTheme', // Activamos nuestro tema oscuro por defecto
    themes: {
    c_mDarkTheme,
    },
},
})