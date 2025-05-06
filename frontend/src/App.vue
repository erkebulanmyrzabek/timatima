<template>
  <div class="app">
    <nav-bar />
    <div class="container">
      <router-view />
    </div>
    <app-footer />
  </div>
</template>

<script>
import NavBar from '@/components/layout/NavBar.vue';
import AppFooter from '@/components/layout/AppFooter.vue';

export default {
  name: 'App',
  components: {
    NavBar,
    AppFooter
  }
}
</script>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: 'Arial', sans-serif;
  background-color: #f5f5f5;
}

.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.container {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 20px;
}
</style> 