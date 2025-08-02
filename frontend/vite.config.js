// import { fileURLToPath, URL } from 'node:url'

// import { defineConfig } from 'vite'
// import vue from '@vitejs/plugin-vue'
// import vueDevTools from 'vite-plugin-vue-devtools'

// // https://vite.dev/config/
// export default defineConfig({
//   plugins: [
//     vue(),
//     // vueDevTools(),
//   ],
//   resolve: {
//     alias: {
//       '@': fileURLToPath(new URL('./src', import.meta.url))
//     },
//   },
// })


// vite.config.js

import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      // --- MODIFICACIÓN 1: ESTRATEGIA DE REGISTRO ---
      // 'prompt' es mejor porque le da al usuario un botón de "actualizar"
      // cuando hay una nueva versión de la app, en lugar de forzar la recarga.
      registerType: 'prompt', 
      
      // --- MODIFICACIÓN 2: INCLUIR EL MANIFEST ---
      // Esto asegura que el manifest.json se genere correctamente.
      includeAssets: ['favicon.ico', 'apple-touch-icon.png'],
      manifest: {
        name: 'Client Manager',
        short_name: 'ClientMgr',
        description: 'Gestión de clientes y saldos offline-first.',
        theme_color: '#212121',
        background_color: '#121212',
        start_url: '.',
        display: 'standalone', // Esto hace que se abra como una app sin la barra del navegador
        icons: [
          // Asegúrate de que estos archivos existan en tu carpeta 'public'
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable' // Importante para una mejor apariencia en Android
          }
        ]
      },
      
      // --- MODIFICACIÓN 3: CONFIGURACIÓN DEL SERVICE WORKER (LA MÁS IMPORTANTE) ---
      workbox: {
        // Esta línea le dice al Service Worker que guarde en caché todos los archivos
        // necesarios para que la aplicación se pueda iniciar sin conexión.
        globPatterns: ['**/*.{js,css,html,png,svg,ico}'],
        
        // Esto pre-cachea los recursos de Google Fonts si los usas.
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'google-fonts-cache',
              expiration: { maxEntries: 10, maxAgeSeconds: 60 * 60 * 24 * 365 }, // 1 año
              cacheableResponse: { statuses: [0, 200] }
            }
          }
        ]
      }
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})