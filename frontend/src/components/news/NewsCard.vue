<template>
  <div class="news-card card">
    <img 
      v-if="news.image" 
      :src="getImageUrl(news.image)" 
      :alt="news.title" 
      class="card-image" 
    />
    <div v-else class="card-image card-image-placeholder">
      <div class="placeholder-text">DOM ADVOKATOV</div>
    </div>
    
    <div class="card-content">
      <h3 class="card-title">{{ news.title }}</h3>
      <p class="card-description">{{ news.short_description }}</p>
      <div class="card-footer">
        <span class="card-date">{{ formatDate(news.published_at) }}</span>
        <router-link :to="`/news/${news.id}`" class="card-link">Подробнее</router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NewsCard',
  props: {
    news: {
      type: Object,
      required: true
    }
  },
  methods: {
    getImageUrl(image) {
      // Проверяем, является ли путь к изображению полным URL
      if (image.startsWith('http')) {
        return image;
      }
      // Если путь относительный, добавляем базовый URL бэкенда
      return `${image}`;
    },
    formatDate(dateString) {
      // Форматирование даты в локализованном виде
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('ru-RU', {
        day: '2-digit',
        month: 'long',
        year: 'numeric'
      }).format(date);
    }
  }
}
</script>

<style scoped>
.news-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s, box-shadow 0.3s;
}

.card-image {
  height: 200px;
  width: 100%;
  object-fit: cover;
}

.card-image-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--primary-color);
  color: rgba(255, 255, 255, 0.8);
}

.placeholder-text {
  font-size: 1.5rem;
  font-weight: 600;
  opacity: 0.7;
}

.card-content {
  padding: 20px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.card-title {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--primary-color);
}

.card-description {
  color: var(--light-text);
  margin-bottom: 20px;
  flex-grow: 1;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

.card-date {
  color: var(--lighter-text);
  font-size: 0.9rem;
}

.card-link {
  color: var(--secondary-color);
  font-weight: 500;
  transition: all 0.3s;
}

.card-link:hover {
  text-decoration: underline;
}

.news-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}
</style> 