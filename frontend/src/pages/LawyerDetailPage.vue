<template>
  <div class="lawyer-detail-page">
    <div class="container">
      <div v-if="loading" class="loading-container">
        <div class="spinner"></div>
      </div>
      
      <div v-else-if="error" class="error-container">
        <p>Произошла ошибка при загрузке информации об адвокате.</p>
        <button class="btn btn-primary" @click="goBack">Вернуться назад</button>
      </div>
      
      <div v-else-if="lawyer" class="lawyer-profile">
        <div class="profile-header">
          <div class="profile-photo-container">
            <img 
              v-if="lawyer.photo" 
              :src="getImageUrl(lawyer.photo)" 
              :alt="`${lawyer.first_name} ${lawyer.last_name}`" 
              class="profile-photo" 
            />
            <div v-else class="profile-photo profile-photo-placeholder">
              <i class="fas fa-user"></i>
            </div>
          </div>
          
          <div class="profile-info">
            <h1 class="profile-name">{{ lawyer.first_name }} {{ lawyer.last_name }}</h1>
            <div class="profile-meta">
              <div class="profile-specialization">{{ lawyer.specialization }}</div>
              <div class="profile-experience">Опыт: {{ lawyer.experience_years }} лет</div>
              <div class="profile-location" v-if="lawyer.city">
                <i class="fas fa-map-marker-alt"></i> {{ lawyer.city }}
              </div>
              <div class="profile-license" v-if="lawyer.license_number">
                № лицензии: {{ lawyer.license_number }}
              </div>
            </div>
            
            <div class="profile-contact">
              <a :href="`tel:${lawyer.phone}`" class="btn btn-primary" v-if="lawyer.phone">
                <i class="fas fa-phone"></i> Позвонить
              </a>
              <a :href="`mailto:${lawyer.email}`" class="btn btn-outline" v-if="lawyer.email">
                <i class="fas fa-envelope"></i> Написать
              </a>
            </div>
          </div>
        </div>
        
        <div class="profile-sections">
          <div class="profile-section">
            <h2>О специалисте</h2>
            <div class="profile-about">
              {{ lawyer.about }}
            </div>
          </div>
          
          <div class="profile-section" v-if="lawyer.education && lawyer.education.length">
            <h2>Образование</h2>
            <ul class="profile-education-list">
              <li v-for="(edu, index) in lawyer.education" :key="index">
                {{ edu.institution }}, {{ edu.degree }}, {{ edu.year }}
              </li>
            </ul>
          </div>
          
          <div class="profile-section" v-if="lawyer.languages && lawyer.languages.length">
            <h2>Языки</h2>
            <div class="profile-languages">
              {{ formatLanguages(lawyer.languages) }}
            </div>
          </div>
          
          <div class="profile-section" v-if="lawyer.expertise && lawyer.expertise.length">
            <h2>Области практики</h2>
            <div class="profile-expertise">
              <div 
                v-for="(item, index) in lawyer.expertise" 
                :key="index"
                class="expertise-item"
              >
                {{ item }}
              </div>
            </div>
          </div>
        </div>
        
        <div class="profile-footer">
          <button class="btn btn-outline" @click="goBack">
            &laquo; Вернуться к списку адвокатов
          </button>
        </div>
      </div>
      
      <div v-else class="not-found-container">
        <h2>Адвокат не найден</h2>
        <p>Запрашиваемый адвокат не существует или был удален.</p>
        <button class="btn btn-primary" @click="goBack">Вернуться к списку адвокатов</button>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRoute, useRouter } from 'vue-router';

export default {
  name: 'LawyerDetailPage',
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
        await store.dispatch('lawyers/fetchLawyerItem', props.id);
      } catch (error) {
        console.error('Ошибка загрузки адвоката:', error);
      }
    });
    
    // Получение URL изображения
    const getImageUrl = (photo) => {
      if (!photo) return null;
      if (photo.startsWith('http')) {
        return photo;
      }
      return `${photo}`;
    };
    
    // Форматирование языков
    const formatLanguages = (languages) => {
      if (!languages || !languages.length) return '';
      return languages.join(', ');
    };
    
    // Возврат назад
    const goBack = () => {
      router.push('/lawyers');
    };
    
    return {
      lawyer: computed(() => store.getters['lawyers/lawyerItem']),
      loading: computed(() => store.getters['lawyers/loading']),
      error: computed(() => store.getters['lawyers/error']),
      getImageUrl,
      formatLanguages,
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

.profile-header {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 30px;
  margin-bottom: 40px;
}

.profile-photo-container {
  border-radius: 8px;
  overflow: hidden;
  height: 300px;
}

.profile-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-photo-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #e0e0e0;
  width: 100%;
  height: 100%;
  font-size: 64px;
  color: #999;
}

.profile-name {
  font-size: 2.2rem;
  margin-bottom: 15px;
}

.profile-meta {
  margin-bottom: 30px;
}

.profile-specialization {
  color: var(--secondary-color);
  font-size: 1.2rem;
  font-weight: 500;
  margin-bottom: 10px;
}

.profile-experience {
  font-size: 1.1rem;
  margin-bottom: 5px;
}

.profile-location,
.profile-license {
  color: var(--light-text);
  margin-bottom: 5px;
}

.profile-contact {
  display: flex;
  gap: 15px;
}

.profile-sections {
  margin-bottom: 40px;
}

.profile-section {
  margin-bottom: 30px;
}

.profile-section h2 {
  margin-bottom: 15px;
  font-size: 1.5rem;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 10px;
}

.profile-about {
  line-height: 1.6;
  white-space: pre-line;
}

.profile-education-list {
  padding-left: 20px;
  line-height: 1.6;
}

.profile-languages {
  line-height: 1.6;
}

.profile-expertise {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.expertise-item {
  background-color: rgba(76, 175, 80, 0.1);
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 0.9rem;
  color: var(--secondary-color);
}

.profile-footer {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .profile-header {
    grid-template-columns: 1fr;
  }
  
  .profile-name {
    font-size: 1.8rem;
  }
  
  .profile-contact {
    flex-direction: column;
  }
  
  .profile-contact .btn {
    width: 100%;
  }
}
</style> 