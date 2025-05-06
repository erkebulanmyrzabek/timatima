<template>
  <div class="register-page">
    <div class="container">
      <div class="auth-form-container">
        <div class="auth-form-header">
          <h1>Регистрация</h1>
          <p>Создайте новый аккаунт, чтобы получить доступ ко всем функциям портала</p>
        </div>
        
        <form class="auth-form" @submit.prevent="handleSubmit">
          <div class="form-group">
            <label class="form-label" for="email">Email:</label>
            <input 
              id="email" 
              v-model="userData.email" 
              type="email" 
              class="form-input" 
              required
              placeholder="Введите ваш email"
            />
          </div>
          
          <div class="form-group">
            <label class="form-label" for="first_name">Имя:</label>
            <input 
              id="first_name" 
              v-model="userData.first_name" 
              type="text" 
              class="form-input" 
              placeholder="Введите ваше имя"
            />
          </div>
          
          <div class="form-group">
            <label class="form-label" for="last_name">Фамилия:</label>
            <input 
              id="last_name" 
              v-model="userData.last_name" 
              type="text" 
              class="form-input" 
              placeholder="Введите вашу фамилию"
            />
          </div>
          
          <div class="form-group">
            <label class="form-label" for="password">Пароль:</label>
            <input 
              id="password" 
              v-model="userData.password" 
              type="password" 
              class="form-input" 
              required
              placeholder="Введите пароль"
            />
          </div>
          
          <div class="form-group">
            <label class="form-label" for="confirm_password">Подтверждение пароля:</label>
            <input 
              id="confirm_password" 
              v-model="confirmPassword" 
              type="password" 
              class="form-input" 
              required
              placeholder="Повторите пароль"
            />
            <div class="form-error" v-if="passwordError">
              {{ passwordError }}
            </div>
          </div>
          
          <div class="form-error" v-if="error">
            {{ error }}
          </div>
          
          <div class="form-actions">
            <button 
              type="submit" 
              class="btn btn-primary btn-block" 
              :disabled="loading || passwordError"
            >
              <span v-if="loading">Регистрация...</span>
              <span v-else>Зарегистрироваться</span>
            </button>
          </div>
          
          <div class="auth-links">
            <p>Уже есть аккаунт? <router-link to="/login">Войти</router-link></p>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

export default {
  name: 'RegisterPage',
  setup() {
    const store = useStore();
    const router = useRouter();
    
    // Данные формы
    const userData = ref({
      email: '',
      first_name: '',
      last_name: '',
      password: ''
    });
    
    const confirmPassword = ref('');
    const passwordError = ref('');
    
    // Состояние
    const loading = computed(() => store.getters['auth/loading']);
    const error = computed(() => store.getters['auth/error']);
    
    // Валидация совпадения паролей
    watch([() => userData.value.password, confirmPassword], ([password, confirm]) => {
      if (password || confirm) {
        passwordError.value = password === confirm ? '' : 'Пароли не совпадают';
      } else {
        passwordError.value = '';
      }
    });
    
    // Обработка формы
    const handleSubmit = async () => {
      if (passwordError.value) return;
      
      try {
        // Регистрация пользователя
        await store.dispatch('auth/register', userData.value);
        
        // После успешной регистрации выполняем вход
        await store.dispatch('auth/login', {
          email: userData.value.email,
          password: userData.value.password
        });
        
        // Перенаправляем на главную страницу
        router.push('/');
      } catch (err) {
        // Обработка ошибок происходит в хранилище
        console.error('Ошибка регистрации:', err);
      }
    };
    
    return {
      userData,
      confirmPassword,
      passwordError,
      loading,
      error,
      handleSubmit
    };
  }
}
</script>

<style scoped>
.register-page {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 0;
}

.auth-form-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  max-width: 450px;
  width: 100%;
  padding: 30px;
  margin: 0 auto;
}

.auth-form-header {
  text-align: center;
  margin-bottom: 30px;
}

.auth-form-header h1 {
  font-size: 1.8rem;
  margin-bottom: 10px;
}

.auth-form-header p {
  color: var(--light-text);
}

.form-group {
  margin-bottom: 20px;
}

.btn-block {
  width: 100%;
  padding: 12px;
  font-size: 1rem;
}

.form-actions {
  margin-top: 30px;
}

.form-error {
  background-color: rgba(244, 67, 54, 0.1);
  color: var(--danger-color);
  padding: 10px;
  border-radius: 4px;
  margin-top: 5px;
}

.auth-links {
  margin-top: 20px;
  text-align: center;
  color: var(--light-text);
}

.auth-links a {
  color: var(--secondary-color);
  text-decoration: none;
  font-weight: 500;
}

.auth-links a:hover {
  text-decoration: underline;
}
</style> 