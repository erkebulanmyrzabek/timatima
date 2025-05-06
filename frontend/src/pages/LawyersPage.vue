<template>
  <div class="lawyers-page">
    <div class="container">
      <div class="page-header">
        <h1>Адвокаты</h1>
        <div class="search-bar">
          <input 
            type="text" 
            v-model="searchQuery" 
            @input="handleSearch" 
            placeholder="Поиск адвокатов..." 
            class="search-input" 
          />
        </div>
      </div>
      
      <div class="filters">
        <div class="filter-item">
          <label for="specialization">Специализация:</label>
          <select 
            id="specialization" 
            v-model="selectedSpecialization"
            @change="applyFilters"
            class="filter-select"
          >
            <option value="">Все специализации</option>
            <option value="Гражданское право">Гражданское право</option>
            <option value="Уголовное право">Уголовное право</option>
            <option value="Административное право">Административное право</option>
            <option value="Семейное право">Семейное право</option>
            <option value="Корпоративное право">Корпоративное право</option>
          </select>
        </div>
      </div>
      
      <div v-if="loading" class="loading-container">
        <div class="spinner"></div>
      </div>
      
      <div v-else>
        <div v-if="lawyers.length === 0" class="no-results">
          <p>Адвокаты не найдены</p>
        </div>
        
        <div v-else class="lawyers-grid grid-cols-3">
          <lawyer-card 
            v-for="lawyer in lawyers" 
            :key="lawyer.id" 
            :lawyer="lawyer" 
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
import LawyerCard from '@/components/lawyers/LawyerCard.vue';

export default {
  name: 'LawyersPage',
  components: {
    LawyerCard
  },
  setup() {
    const store = useStore();
    const route = useRoute();
    const router = useRouter();
    
    // Параметры и состояние
    const searchQuery = ref('');
    const searchTimeout = ref(null);
    const selectedSpecialization = ref('');
    
    // Получаем параметры из URL
    const currentPage = computed(() => {
      const page = parseInt(route.query.page) || 1;
      return page > 0 ? page : 1;
    });
    
    // Загрузка данных
    const fetchLawyersWithParams = async () => {
      await store.dispatch('lawyers/fetchLawyers', {
        page: currentPage.value,
        limit: 9,
        specialization: selectedSpecialization.value || null
      });
    };
    
    // Загрузка данных при монтировании компонента
    onMounted(fetchLawyersWithParams);
    
    // Наблюдение за изменением страницы
    watch(currentPage, () => {
      fetchLawyersWithParams();
    });
    
    // Обработка поиска с debounce
    const handleSearch = () => {
      if (searchTimeout.value) {
        clearTimeout(searchTimeout.value);
      }
      
      searchTimeout.value = setTimeout(() => {
        // Сбрасываем на первую страницу при поиске
        router.push({ query: { ...route.query, page: 1 } });
        fetchLawyersWithParams();
      }, 500);
    };
    
    // Применение фильтров
    const applyFilters = () => {
      router.push({ query: { ...route.query, page: 1 } });
      fetchLawyersWithParams();
    };
    
    // Изменение страницы
    const changePage = (page) => {
      router.push({ query: { ...route.query, page } });
    };
    
    // Генерация видимых номеров страниц
    const visiblePageNumbers = computed(() => {
      const totalPages = store.getters['lawyers/totalPages'];
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
      lawyers: computed(() => store.getters['lawyers/allLawyers']),
      loading: computed(() => store.getters['lawyers/loading']),
      error: computed(() => store.getters['lawyers/error']),
      totalPages: computed(() => store.getters['lawyers/totalPages']),
      currentPage,
      searchQuery,
      selectedSpecialization,
      handleSearch,
      applyFilters,
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
  margin-bottom: 20px;
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

.filters {
  margin-bottom: 30px;
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  min-width: 200px;
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

.lawyers-grid {
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