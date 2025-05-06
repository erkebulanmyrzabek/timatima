<template>
  <div class="news-detail-page">
    <div class="container">
      <div v-if="loading" class="loading-container">
        <div class="spinner"></div>
      </div>
      
      <div v-else-if="error" class="error-container">
        <p>Произошла ошибка при загрузке новости.</p>
        <button class="btn btn-primary" @click="goBack">Вернуться назад</button>
      </div>
      
      <div v-else-if="newsItem" class="news-content">
        <div class="news-header">
          <h1 class="news-title">{{ newsItem.title }}</h1>
          <div class="news-meta">
            <span class="news-date">{{ formatDate(newsItem.published_at) }}</span>
          </div>
        </div>
        
        <div class="news-image-container" v-if="newsItem.image">
          <img :src="getImageUrl(newsItem.image)" :alt="newsItem.title" class="news-image" />
        </div>
        
        <div class="news-description">
          {{ newsItem.short_description }}
        </div>
        
        <div class="news-body" v-html="newsItem.content"></div>
        
        <div class="news-video" v-if="newsItem.video_url">
          <h3>Видео</h3>
          <div class="video-container">
            <iframe 
              :src="getEmbedVideoUrl(newsItem.video_url)" 
              frameborder="0" 
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
              allowfullscreen
            ></iframe>
          </div>
        </div>
        
        <div class="news-footer">
          <button class="btn btn-outline" @click="goBack">
            &laquo; Вернуться к списку новостей
          </button>
        </div>
      </div>
      
      <div v-else class="not-found-container">
        <h2>Новость не найдена</h2>
        <p>Запрашиваемая новость не существует или была удалена.</p>
        <button class="btn btn-primary" @click="goBack">Вернуться к списку новостей</button>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRoute, useRouter } from 'vue-router';

export default {
  name: 'NewsDetailPage',
  props: {
    id: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const store = useStore();
    const route = useRoute();
    const router = useRouter();
    
    // Загрузка данных при монтировании компонента
    onMounted(async () => {
      try {
        await store.dispatch('news/fetchNewsItem', props.id);
      } catch (error) {
        console.error('Ошибка загрузки новости:', error);
      }
    });
    
    // Форматирование даты
    const formatDate = (dateString) => {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    };
    
    // Получение URL изображения
    const getImageUrl = (image) => {
      if (image.startsWith('http')) {
        return image;
      }
      return `${image}`;
    };
    
    // Преобразование URL видео для встраивания
    const getEmbedVideoUrl = (url) => {
      if (!url) return '';
      
      // YouTube
      let match = url.match(/(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)/);
      if (match) {
        return `https://www.youtube.com/embed/${match[1]}`;
      }
      
      // YouTube short url
      match = url.match(/(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^?]+)/);
      if (match) {
        return `https://www.youtube.com/embed/${match[1]}`;
      }
      
      // Vimeo
      match = url.match(/(?:https?:\/\/)?(?:www\.)?vimeo\.com\/(\d+)/);
      if (match) {
        return `https://player.vimeo.com/video/${match[1]}`;
      }
      
      return url;
    };
    
    // Возврат назад
    const goBack = () => {
      router.push('/news');
    };
    
    return {
      newsItem: computed(() => store.getters['news/newsItem']),
      loading: computed(() => store.getters['news/loading']),
      error: computed(() => store.getters['news/error']),
      formatDate,
      getImageUrl,
      getEmbedVideoUrl,
      goBack
    };
  }
}
</script>

<style scoped>
.loading-container {
  display: flex;
  justify-content: center;
  padding: 100px 0;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(76, 175, 80, 0.3);
  border-radius: 50%;
  border-top-color: var(--secondary-color);
  animation: spin 1s linear infinite;
}

.error-container,
.not-found-container {
  text-align: center;
  padding: 60px 0;
}

.news-header {
  margin-bottom: 30px;
}

.news-title {
  font-size: 2.5rem;
  margin-bottom: 15px;
  line-height: 1.2;
}

.news-meta {
  color: var(--light-text);
  font-size: 0.9rem;
}

.news-image-container {
  margin-bottom: 30px;
}

.news-image {
  width: 100%;
  max-height: 500px;
  object-fit: cover;
  border-radius: 8px;
}

.news-description {
  font-size: 1.2rem;
  line-height: 1.6;
  margin-bottom: 30px;
  color: var(--light-text);
  font-weight: 500;
}

.news-body {
  font-size: 1.1rem;
  line-height: 1.8;
  margin-bottom: 40px;
}

.news-body h2 {
  margin-top: 30px;
  margin-bottom: 15px;
}

.news-body p {
  margin-bottom: 20px;
}

.news-body img {
  max-width: 100%;
  border-radius: 8px;
  margin: 20px 0;
}

.news-video {
  margin-bottom: 40px;
}

.video-container {
  position: relative;
  padding-bottom: 56.25%; /* 16:9 */
  height: 0;
  overflow: hidden;
  max-width: 100%;
}

.video-container iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 8px;
}

.news-footer {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-start;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .news-title {
    font-size: 2rem;
  }
  
  .news-description {
    font-size: 1.1rem;
  }
  
  .news-body {
    font-size: 1rem;
  }
}
</style> 