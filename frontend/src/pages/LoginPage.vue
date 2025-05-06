<template>
  <div class="login-page">
    <div class="container">
      <div class="auth-form-container">
        <div class="auth-form-header">
          <h1>Вход в аккаунт</h1>
          <p>Войдите в свой аккаунт, чтобы получить доступ ко всем функциям портала</p>
        </div>
        
        <form class="auth-form" @submit.prevent="handleSubmit">
          <div class="form-group">
            <label class="form-label" for="email">Email:</label>
            <input 
              id="email" 
              v-model="credentials.email" 
              type="email" 
              class="form-input" 
              required
              placeholder="Введите ваш email"
            />
          </div>
          
          <div class="form-group">
            <label class="form-label" for="password">Пароль:</label>
            <input 
              id="password" 
              v-model="credentials.password" 
              type="password" 
              class="form-input" 
              required
              placeholder="Введите пароль"
            />
          </div>
          
          <div class="form-error" v-if="error">
            {{ error }}
          </div>
          
          <div class="form-actions">
            <button 
              type="submit" 
              class="btn btn-primary btn-block" 
              :disabled="loading"
            >
              <span v-if="loading">Вход...</span>
              <span v-else>Войти</span>
            </button>
          </div>
          
          <div class="auth-links">
            <p>Нет аккаунта? <router-link to="/register">Зарегистрироваться</router-link></p>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import { useStore } from 'vuex';
import { useRouter, useRoute } from 'vue-router';

export default {
  name: 'LoginPage',
  setup() {
    const store = useStore();
    const router = useRouter();
    const route = useRoute();
    
    // Данные формы
    const credentials = ref({
      email: '',
      password: ''
    });
    
    // Состояние
    const loading = computed(() => store.getters['auth/loading']);
    const error = computed(() => store.getters['auth/error']);
    const redirectPath = computed(() => route.query.redirect || '/');
    
    // Обработка формы
    const handleSubmit = async () => {
      try {
        await store.dispatch('auth/login', credentials.value);
        
        // После успешного входа перенаправляем пользователя
        router.push(redirectPath.value);
      } catch (err) {
        // Обработка ошибок происходит в хранилище
        console.error('Ошибка входа:', err);
      }
    };
    
    return {
      credentials,
      loading,
      error,
      handleSubmit
    };
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 70vh;
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
  margin-bottom: 20px;
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