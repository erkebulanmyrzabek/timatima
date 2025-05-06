<template>
  <div class="news-page">
    <div class="container">
      <div class="page-header">
        <h1>Новости</h1>
        <div class="search-bar">
          <input 
            type="text" 
            v-model="searchQuery" 
            @input="handleSearch" 
            placeholder="Поиск новостей..." 
            class="search-input" 
          />
        </div>
      </div>
      
      <div v-if="loading" class="loading-container">
        <div class="spinner"></div>
      </div>
      
      <div v-else>
        <div v-if="news.length === 0" class="no-results">
          <p>Новости не найдены</p>
        </div>
        
        <div v-else class="news-grid grid-cols-3">
          <news-card 
            v-for="item in news" 
            :key="item.id" 
            :news="item" 
          />
        </div>
        
        <div class="pagination" v-if="totalPages > 1">
          <button 
            class="pagination-btn" 
            :disabled="currentPage === 1" 
            @click="changePage(currentPage - 1)"
          >
            &laquo; Предыдущая
          </button>
          
          <div class="pagination-pages">
            <button 
              v-for="page in visiblePageNumbers" 
              :key="page" 
              class="pagination-page" 
              :class="{ active: page === currentPage }"
              @click="changePage(page)"
            >
              {{ page }}
            </button>
          </div>
          
          <button 
            class="pagination-btn" 
            :disabled="currentPage === totalPages" 
            @click="changePage(currentPage + 1)"
          >
            Следующая &raquo;
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useStore } from 'vuex';
import { useRoute, useRouter } from 'vue-router';
import NewsCard from '@/components/news/NewsCard.vue';

export default {
  name: 'NewsPage',
  components: {
    NewsCard
  },
  setup() {
    const store = useStore();
    const route = useRoute();
    const router = useRouter();
    
    // Параметры и состояние
    const searchQuery = ref('');
    const searchTimeout = ref(null);
    
    // Получаем параметры из URL
    const currentPage = computed(() => {
      const page = parseInt(route.query.page) || 1;
      return page > 0 ? page : 1;
    });
    
    // Загрузка данных
    const fetchNewsWithParams = async () => {
      await store.dispatch('news/fetchNews', {
        page: currentPage.value,
        limit: 9,
        search: searchQuery.value
      });
    };
    
    // Загрузка данных при монтировании компонента
    onMounted(fetchNewsWithParams);
    
    // Наблюдение за изменением страницы
    watch(currentPage, () => {
      fetchNewsWithParams();
    });
    
    // Обработка поиска с debounce
    const handleSearch = () => {
      if (searchTimeout.value) {
        clearTimeout(searchTimeout.value);
      }
      
      searchTimeout.value = setTimeout(() => {
        // Сбрасываем на первую страницу при поиске
        router.push({ query: { ...route.query, page: 1 } });
        fetchNewsWithParams();
      }, 500);
    };
    
    // Изменение страницы
    const changePage = (page) => {
      router.push({ query: { ...route.query, page } });
    };
    
    // Генерация видимых номеров страниц
    const visiblePageNumbers = computed(() => {
      const totalPages = store.getters['news/totalPages'];
      if (totalPages <= 7) {
        return [...Array(totalPages)].map((_, i) => i + 1);
      }
      
      const current = currentPage.value;
      const pages = [];
      
      if (current <= 3) {
        // Начало: 1 2 3 4 5 ... totalPages
        for (let i = 1; i <= 5; i++) {
          pages.push(i);
        }
        pages.push('...');
        pages.push(totalPages);
      } else if (current >= totalPages - 2) {
        // Конец: 1 ... totalPages-4 totalPages-3 totalPages-2 totalPages-1 totalPages
        pages.push(1);
        pages.push('...');
        for (let i = totalPages - 4; i <= totalPages; i++) {
          pages.push(i);
        }
      } else {
        // Середина: 1 ... current-1 current current+1 ... totalPages
        pages.push(1);
        pages.push('...');
        for (let i = current - 1; i <= current + 1; i++) {
          pages.push(i);
        }
        pages.push('...');
        pages.push(totalPages);
      }
      
      return pages;
    });
    
    return {
      news: computed(() => store.getters['news/allNews']),
      loading: computed(() => store.getters['news/loading']),
      error: computed(() => store.getters['news/error']),
      totalPages: computed(() => store.getters['news/totalPages']),
      currentPage,
      searchQuery,
      handleSearch,
      changePage,
      visiblePageNumbers
    };
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.search-bar {
  width: 300px;
}

.search-input {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
}

.loading-container {
  display: flex;
  justify-content: center;
  padding: 60px 0;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(76, 175, 80, 0.3);
  border-radius: 50%;
  border-top-color: var(--secondary-color);
  animation: spin 1s linear infinite;
}

.no-results {
  text-align: center;
  padding: 40px 0;
  color: var(--light-text);
}

.news-grid {
  margin-bottom: 40px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 30px;
  margin-bottom: 60px;
}

.pagination-btn {
  background-color: transparent;
  border: 1px solid var(--border-color);
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.pagination-btn:hover:not(:disabled) {
  background-color: var(--primary-color);
  color: white;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-pages {
  display: flex;
  margin: 0 10px;
}

.pagination-page {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 4px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: transparent;
  cursor: pointer;
  transition: all 0.3s;
}

.pagination-page:hover {
  background-color: rgba(26, 58, 52, 0.1);
}

.pagination-page.active {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .search-bar {
    width: 100%;
    margin-top: 15px;
  }
  
  .pagination {
    flex-direction: column;
    gap: 15px;
  }
}
</style> 