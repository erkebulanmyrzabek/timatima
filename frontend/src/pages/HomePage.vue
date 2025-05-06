<template>
  <div class="home-page">
    <section class="hero-section">
      <div class="container">
        <h1>Дом Адвокатов</h1>
        <p class="subtitle">Профессиональная юридическая помощь и консультации от опытных адвокатов</p>
      </div>
    </section>
    
    <section class="news-section">
      <div class="container">
        <div class="section-header">
          <h2>Новости в мире права</h2>
          <router-link to="/news" class="section-link">Все новости</router-link>
        </div>
        
        <div v-if="newsLoading" class="loading-spinner">
          <div class="spinner"></div>
        </div>
        
        <div v-else class="news-grid grid-cols-3">
          <news-card 
            v-for="news in featuredNews" 
            :key="news.id" 
            :news="news" 
          />
        </div>
      </div>
    </section>
    
    <section class="lawyers-section">
      <div class="container">
        <div class="section-header">
          <h2>Список лучших адвокатов</h2>
          <router-link to="/lawyers" class="section-link">Все адвокаты</router-link>
        </div>
        
        <div v-if="lawyersLoading" class="loading-spinner">
          <div class="spinner"></div>
        </div>
        
        <div v-else class="lawyers-grid grid-cols-3">
          <lawyer-card 
            v-for="lawyer in featuredLawyers" 
            :key="lawyer.id" 
            :lawyer="lawyer"
          />
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import NewsCard from '@/components/news/NewsCard.vue';
import LawyerCard from '@/components/lawyers/LawyerCard.vue';

export default {
  name: 'HomePage',
  components: {
    NewsCard,
    LawyerCard
  },
  setup() {
    const store = useStore();
    
    // Загрузка данных при монтировании компонента
    onMounted(() => {
      store.dispatch('news/fetchFeaturedNews');
      store.dispatch('lawyers/fetchFeaturedLawyers');
    });
    
    // Вычисляемые свойства
    const featuredNews = computed(() => store.getters['news/featuredNews']);
    const newsLoading = computed(() => store.getters['news/loading']);
    
    const featuredLawyers = computed(() => store.getters['lawyers/featuredLawyers']);
    const lawyersLoading = computed(() => store.getters['lawyers/loading']);
    
    return {
      featuredNews,
      newsLoading,
      featuredLawyers,
      lawyersLoading
    };
  }
}
</script>

<style scoped>
.hero-section {
  background: linear-gradient(rgba(26, 58, 52, 0.9), rgba(26, 58, 52, 0.8)), url('@/assets/images/hero-bg.jpg');
  background-size: cover;
  background-position: center;
  color: white;
  padding: 100px 0;
  text-align: center;
  margin-bottom: 40px;
}

.hero-section h1 {
  font-size: 3rem;
  margin-bottom: 20px;
  color: white;
}

.subtitle {
  font-size: 1.2rem;
  max-width: 600px;
  margin: 0 auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.section-link {
  color: var(--secondary-color);
  font-weight: 500;
  transition: color 0.3s;
}

.section-link:hover {
  text-decoration: underline;
}

.news-section,
.lawyers-section {
  margin-bottom: 60px;
}

.loading-spinner {
  display: flex;
  justify-content: center;
  padding: 40px 0;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(76, 175, 80, 0.3);
  border-radius: 50%;
  border-top-color: var(--secondary-color);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .hero-section h1 {
    font-size: 2.5rem;
  }
  
  .subtitle {
    font-size: 1rem;
  }
}
</style> 