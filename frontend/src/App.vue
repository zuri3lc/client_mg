<script setup>
import { RouterView } from 'vue-router'
import GlobalFeedback from './components/GlobalFeedback.vue';
import { onMounted } from 'vue';
import { startAutoSyncService } from '@/services/autoSync';

onMounted(() => {
    // Iniciamos el servicio silencioso
    startAutoSyncService();
});
</script>
<template>
  <v-app>
      <RouterView />
    <GlobalFeedback />
  </v-app>
</template>
<style>
  
html, body, #app {
  height: 100%;
  user-select: none;
  -webkit-tap-highlight-color: transparent; 
  background-color: #0a0a0aff;
  overscroll-behavior: none;
}
.v-application {
  padding-top: calc(env(safe-area-inset-top) + 12px); 
  padding-bottom: env(safe-area-inset-bottom);
  height: 100%; 
  display: flex;
  flex-direction: column;
}
.v-app-bar {
    padding-top: calc(env(safe-area-inset-top) + 15px);
    height: auto !important; /* Dejar que crezca lo necesario */
}
.v-app-bar .v-toolbar__content {
    height: 50px !important; /* Altura estándar MD3 */
}
/* Permitir selección en inputs */
input, textarea {
  user-select: text;
}
</style>