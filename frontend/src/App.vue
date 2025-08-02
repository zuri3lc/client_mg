<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
html, body, #app {
  height: 100%; /* Asegura que html, body y el elemento #app ocupen el 100% de la altura */
  margin: 0;
  padding: 0;
  background-color: #0a0a0aff;
}
</style>