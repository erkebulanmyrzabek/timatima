<template>
  <div class="lawyer-card card">
    <div class="lawyer-image-container">
      <img 
        v-if="lawyer.photo" 
        :src="getImageUrl(lawyer.photo)" 
        :alt="`${lawyer.first_name} ${lawyer.last_name}`" 
        class="lawyer-image" 
      />
      <div v-else class="lawyer-image lawyer-image-placeholder">
        <div class="placeholder-icon">
          <i class="fas fa-user"></i>
        </div>
      </div>
      <div class="lawyer-experience">
        {{ lawyer.experience_years }} лет опыта
      </div>
    </div>
    
    <div class="card-content">
      <h3 class="lawyer-name">{{ lawyer.first_name }} {{ lawyer.last_name }}</h3>
      <div class="lawyer-specialization">{{ lawyer.specialization }}</div>
      <div class="lawyer-location" v-if="lawyer.city">
        <i class="fas fa-map-marker-alt"></i> {{ lawyer.city }}
      </div>
      
      <div class="lawyer-description">
        {{ truncateDescription(lawyer.about) }}
      </div>
      
      <div class="lawyer-languages" v-if="lawyer.languages && lawyer.languages.length">
        <span class="language-label">Языки:</span>
        <span class="language-list">{{ formatLanguages(lawyer.languages) }}</span>
      </div>
      
      <div class="card-actions">
        <router-link :to="`/lawyers/${lawyer.id}`" class="btn btn-primary">
          Подробнее
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LawyerCard',
  props: {
    lawyer: {
      type: Object,
      required: true
    }
  },
  methods: {
    getImageUrl(photo) {
      // Проверяем, является ли путь к изображению полным URL
      if (photo.startsWith('http')) {
        return photo;
      }
      // Если путь относительный, добавляем базовый URL бэкенда
      return `${photo}`;
    },
    truncateDescription(description) {
      if (!description) return '';
      if (description.length <= 100) return description;
      return description.slice(0, 100) + '...';
    },
    formatLanguages(languages) {
      if (!languages || !languages.length) return '';
      return languages.join(', ');
    }
  }
}
</script>

<style scoped>
.lawyer-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s, box-shadow 0.3s;
}

.lawyer-image-container {
  position: relative;
}

.lawyer-image {
  height: 200px;
  width: 100%;
  object-fit: cover;
}

.lawyer-image-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #e0e0e0;
  height: 200px;
}

.placeholder-icon {
  font-size: 48px;
  color: #999;
}

.lawyer-experience {
  position: absolute;
  bottom: 0;
  right: 0;
  background-color: var(--secondary-color);
  color: white;
  padding: 5px 10px;
  font-size: 0.9rem;
  font-weight: 500;
}

.card-content {
  padding: 20px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.lawyer-name {
  margin-top: 0;
  margin-bottom: 5px;
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--primary-color);
}

.lawyer-specialization {
  color: var(--secondary-color);
  margin-bottom: 10px;
  font-weight: 500;
}

.lawyer-location {
  color: var(--light-text);
  margin-bottom: 15px;
  font-size: 0.9rem;
}

.lawyer-description {
  color: var(--light-text);
  margin-bottom: 15px;
  flex-grow: 1;
}

.lawyer-languages {
  margin-bottom: 20px;
  font-size: 0.9rem;
}

.language-label {
  color: var(--lighter-text);
}

.language-list {
  color: var(--light-text);
}

.card-actions {
  margin-top: auto;
}

.lawyer-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}
</style> 