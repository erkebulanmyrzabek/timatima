<template>
  <div class="profile-page">
    <div class="container">
      <div class="profile-header">
        <h1>Профиль пользователя</h1>
      </div>
      
      <div class="profile-content">
        <div class="profile-card">
          <div class="profile-info">
            <h2>Личная информация</h2>
            
            <div v-if="loading" class="loading-spinner">
              <div class="spinner"></div>
            </div>
            
            <form v-else @submit.prevent="updateProfile" class="profile-form">
              <div class="form-group">
                <label class="form-label" for="email">Email:</label>
                <input 
                  id="email" 
                  type="email" 
                  v-model="userProfile.email" 
                  class="form-input" 
                  disabled
                />
              </div>
              
              <div class="form-group">
                <label class="form-label" for="first_name">Имя:</label>
                <input 
                  id="first_name" 
                  type="text" 
                  v-model="userProfile.first_name" 
                  class="form-input" 
                  placeholder="Введите ваше имя"
                />
              </div>
              
              <div class="form-group">
                <label class="form-label" for="last_name">Фамилия:</label>
                <input 
                  id="last_name" 
                  type="text" 
                  v-model="userProfile.last_name" 
                  class="form-input" 
                  placeholder="Введите вашу фамилию"
                />
              </div>
              
              <div class="form-error" v-if="error">
                {{ error }}
              </div>
              
              <div class="form-actions">
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  Сохранить изменения
                </button>
              </div>
            </form>
          </div>
        </div>
        
        <div class="profile-card">
          <div class="password-change">
            <h2>Изменение пароля</h2>
            
            <form @submit.prevent="changePassword" class="password-form">
              <div class="form-group">
                <label class="form-label" for="current_password">Текущий пароль:</label>
                <input 
                  id="current_password" 
                  type="password" 
                  v-model="passwordData.current_password" 
                  class="form-input" 
                  required
                />
              </div>
              
              <div class="form-group">
                <label class="form-label" for="new_password">Новый пароль:</label>
                <input 
                  id="new_password" 
                  type="password" 
                  v-model="passwordData.new_password" 
                  class="form-input" 
                  required
                />
              </div>
              
              <div class="form-group">
                <label class="form-label" for="confirm_password">Подтверждение нового пароля:</label>
                <input 
                  id="confirm_password" 
                  type="password" 
                  v-model="passwordData.confirm_password" 
                  class="form-input" 
                  required
                />
              </div>
              
              <div class="form-error" v-if="passwordError">
                {{ passwordError }}
              </div>
              
              <div class="form-actions">
                <button type="submit" class="btn btn-primary" :disabled="passwordLoading">
                  Изменить пароль
                </button>
              </div>
            </form>
          </div>
        </div>
        
        <div class="profile-card danger-zone">
          <h2>Опасная зона</h2>
          <p>Внимание! Эти действия необратимы:</p>
          
          <button 
            class="btn btn-danger" 
            @click="confirmDeleteAccount"
          >
            Удалить аккаунт
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

export default {
  name: 'ProfilePage',
  setup() {
    const store = useStore();
    const router = useRouter();
    
    // Данные пользователя
    const userProfile = ref({
      email: '',
      first_name: '',
      last_name: ''
    });
    
    // Данные для смены пароля
    const passwordData = ref({
      current_password: '',
      new_password: '',
      confirm_password: ''
    });
    
    // Состояние
    const loading = computed(() => store.getters['auth/loading']);
    const error = computed(() => store.getters['auth/error']);
    const passwordLoading = ref(false);
    const passwordError = ref('');
    
    // Загрузка данных пользователя
    onMounted(() => {
      const user = store.getters['auth/user'];
      if (user) {
        userProfile.value = {
          email: user.email || '',
          first_name: user.first_name || '',
          last_name: user.last_name || ''
        };
      } else {
        // Если пользователь не загружен, перенаправляем на страницу входа
        router.push('/login');
      }
    });
    
    // Обновление профиля
    const updateProfile = async () => {
      try {
        await store.dispatch('auth/updateProfile', {
          first_name: userProfile.value.first_name,
          last_name: userProfile.value.last_name
        });
        
        alert('Профиль успешно обновлен');
      } catch (err) {
        console.error('Ошибка обновления профиля:', err);
      }
    };
    
    // Изменение пароля
    const changePassword = async () => {
      passwordError.value = '';
      
      // Проверка совпадения паролей
      if (passwordData.value.new_password !== passwordData.value.confirm_password) {
        passwordError.value = 'Пароли не совпадают';
        return;
      }
      
      passwordLoading.value = true;
      
      try {
        // В реальном проекте здесь будет вызов API для смены пароля
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Очистка формы
        passwordData.value = {
          current_password: '',
          new_password: '',
          confirm_password: ''
        };
        
        alert('Пароль успешно изменен');
      } catch (err) {
        passwordError.value = 'Ошибка при изменении пароля';
        console.error('Ошибка изменения пароля:', err);
      } finally {
        passwordLoading.value = false;
      }
    };
    
    // Подтверждение удаления аккаунта
    const confirmDeleteAccount = () => {
      if (confirm('Вы уверены, что хотите удалить свой аккаунт? Это действие невозможно отменить.')) {
        deleteAccount();
      }
    };
    
    // Удаление аккаунта
    const deleteAccount = async () => {
      try {
        await store.dispatch('auth/deleteAccount');
        router.push('/');
      } catch (err) {
        console.error('Ошибка удаления аккаунта:', err);
        alert('Произошла ошибка при удалении аккаунта. Попробуйте позже.');
      }
    };
    
    return {
      userProfile,
      passwordData,
      loading,
      error,
      passwordLoading,
      passwordError,
      updateProfile,
      changePassword,
      confirmDeleteAccount
    };
  }
}
</script>

<style scoped>
.profile-page {
  padding: 40px 0;
}

.profile-header {
  margin-bottom: 30px;
}

.profile-content {
  display: grid;
  gap: 30px;
}

.profile-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 25px;
}

.profile-card h2 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 1.5rem;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 10px;
}

.loading-spinner {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(76, 175, 80, 0.3);
  border-radius: 50%;
  border-top-color: var(--secondary-color);
  animation: spin 1s linear infinite;
}

.form-actions {
  margin-top: 25px;
}

.form-error {
  background-color: rgba(244, 67, 54, 0.1);
  color: var(--danger-color);
  padding: 10px;
  border-radius: 4px;
  margin-top: 15px;
}

.danger-zone {
  border: 1px solid rgba(244, 67, 54, 0.2);
}

.danger-zone h2 {
  color: var(--danger-color);
}

.btn-danger {
  background-color: var(--danger-color);
  color: white;
}

.btn-danger:hover {
  background-color: rgb(200, 55, 45);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (min-width: 768px) {
  .profile-content {
    grid-template-columns: 1fr 1fr;
  }
  
  .danger-zone {
    grid-column: span 2;
  }
}
</style> 