<template>
  <div class="not-found-page">
    <div class="container">
      <div class="not-found-content">
        <h1>404</h1>
        <h2>Страница не найдена</h2>
        <p>Запрашиваемая страница не существует или была удалена.</p>
        <router-link to="/" class="btn btn-primary">
          Вернуться на главную
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFoundPage'
}
</script>

<style scoped>
.not-found-page {
  padding: 80px 0;
  text-align: center;
}

.not-found-content {
  max-width: 600px;
  margin: 0 auto;
}

h1 {
  font-size: 8rem;
  color: var(--primary-color);
  margin: 0;
  opacity: 0.5;
}

h2 {
  font-size: 2rem;
  margin-bottom: 20px;
}

p {
  margin-bottom: 30px;
  color: var(--light-text);
  font-size: 1.1rem;
}
</style> 