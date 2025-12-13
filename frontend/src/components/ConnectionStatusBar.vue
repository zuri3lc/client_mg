<script setup>
import { useConnectionStore } from '@/stores/connection';
import { computed } from 'vue';

const connectionStore = useConnectionStore();

const status = computed(() => connectionStore.connectionStatus);

</script>

<template>
    <!-- La barra se muestra siempre, pero cambia de color -->
    <div 
        class="connection-status-bar"
        :style="{ 
            backgroundColor: status.color,
            boxShadow: `0 0 10px ${status.color}80` 
        }"
        :class="{ 'pulse-animation': status.pulse }"
    >
        <!-- Shimmer effect overlay -->
        <div class="shimmer"></div>
    </div>
</template>

<style scoped>
.connection-status-bar {
    width: 100%;
    height: 10px; /* Altura solicitada */
    transition: background-color 0.5s ease, box-shadow 0.5s ease;
    position: relative;
    overflow: hidden;
    z-index: 999; /* Asegurar que se vea */
}

.pulse-animation {
    animation: pulse 1s infinite alternate;
}

.shimmer {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        to right, 
        transparent 0%, 
        rgba(255, 255, 255, 0.2) 50%, 
        transparent 100%
    );
    transform: skewX(-20deg) translateX(-150%);
    animation: shimmer 3s infinite;
}

@keyframes pulse {
    0% { opacity: 1; }
    100% { opacity: 0.6; }
}

@keyframes shimmer {
    0% { transform: skewX(-20deg) translateX(-150%); }
    50% { transform: skewX(-20deg) translateX(150%); }
    100% { transform: skewX(-20deg) translateX(150%); }
}
</style>
