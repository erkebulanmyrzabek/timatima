import axios from 'axios';
import apiClient from '@/services/api';

// Начальное состояние
const state = {
  token: localStorage.getItem('token') || null,
  refreshToken: localStorage.getItem('refreshToken') || null,
  user: JSON.parse(localStorage.getItem('user')) || null,
  loading: false,
  error: null,
  pgpPassword: localStorage.getItem('pgpPassword') || null
};

// Геттеры
const getters = {
  isAuthenticated: state => !!state.token,
  token: state => state.token,
  user: state => state.user,
  loading: state => state.loading,
  error: state => state.error,
  pgpPassword: state => state.pgpPassword
};

// Мутации
const mutations = {
  AUTH_START(state) {
    state.loading = true;
    state.error = null;
  },
  AUTH_SUCCESS(state, { token, refreshToken, user }) {
    state.token = token;
    state.refreshToken = refreshToken;
    state.user = user;
    state.loading = false;
    state.error = null;
  },
  AUTH_ERROR(state, error) {
    state.loading = false;
    state.error = error;
  },
  LOGOUT(state) {
    state.token = null;
    state.refreshToken = null;
    state.user = null;
    state.pgpPassword = null;
  },
  UPDATE_USER(state, user) {
    state.user = { ...state.user, ...user };
  },
  SET_PGP_PASSWORD(state, password) {
    state.pgpPassword = password;
    localStorage.setItem('pgpPassword', password);
  }
};

// Действия
const actions = {
  // Регистрация
  async register({ commit }, userData) {
    commit('AUTH_START');
    try {
      console.log('Отправка данных регистрации:', userData);
      
      // Отправляем запрос на регистрацию
      const response = await apiClient.post('/api/auth/register/', userData);
      
      console.log('Ответ сервера на регистрацию:', response.data);
      
      // После успешной регистрации сохраняем токены и данные пользователя
      const token = response.data.access;
      const refreshToken = response.data.refresh;
      const user = {
        id: response.data.id,
        email: response.data.email,
        first_name: response.data.first_name,
        last_name: response.data.last_name,
        is_staff: response.data.is_staff
      };
      
      // Сохраняем токены и данные пользователя
      localStorage.setItem('token', token);
      localStorage.setItem('refreshToken', refreshToken);
      localStorage.setItem('user', JSON.stringify(user));
      
      // Устанавливаем токен авторизации в заголовки по умолчанию
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      commit('AUTH_SUCCESS', { token, refreshToken, user });
      return response.data;
    } catch (error) {
      console.error('Ошибка регистрации:', error);
      
      // Обрабатываем ошибки от сервера
      const errorMessage = error.response 
        ? (error.response.data.detail || error.response.data) 
        : 'Ошибка регистрации. Пожалуйста, попробуйте позже.';
      
      commit('AUTH_ERROR', errorMessage);
      throw error;
    }
  },
  
  // Авторизация
  async login({ commit }, credentials) {
    commit('AUTH_START');
    try {
      const response = await apiClient.post('/api/auth/login/', credentials);
      
      const token = response.data.access;
      const refreshToken = response.data.refresh;
      const user = {
        id: response.data.id,
        email: response.data.email,
        first_name: response.data.first_name,
        last_name: response.data.last_name,
        is_staff: response.data.is_staff
      };
      
      // Сохраняем токены и данные пользователя
      localStorage.setItem('token', token);
      localStorage.setItem('refreshToken', refreshToken);
      localStorage.setItem('user', JSON.stringify(user));
      
      // Устанавливаем токен авторизации в заголовки по умолчанию
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      commit('AUTH_SUCCESS', { token, refreshToken, user });
      return response.data;
    } catch (error) {
      commit('AUTH_ERROR', error.response ? error.response.data : 'Ошибка авторизации');
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
      throw error;
    }
  },
  
  // Обновление токена
  async refreshToken({ commit, state }) {
    if (!state.refreshToken) return;
    
    try {
      const response = await apiClient.post('/api/auth/refresh/', {
        refresh: state.refreshToken
      });
      
      const token = response.data.access;
      
      // Обновляем токен в хранилище
      localStorage.setItem('token', token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      commit('AUTH_SUCCESS', { 
        token, 
        refreshToken: state.refreshToken, 
        user: state.user 
      });
      
      return response.data;
    } catch (error) {
      // Если обновление токена не удалось, выходим из системы
      commit('LOGOUT');
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
      throw error;
    }
  },
  
  // Выход из системы
  logout({ commit, dispatch }) {
    commit('LOGOUT');
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    localStorage.removeItem('pgpPassword'); // Очищаем и пароль от PGP
    
    // Очищаем все ключи в памяти
    dispatch('pgp/clearAllKeys', null, { root: true });
    
    delete axios.defaults.headers.common['Authorization'];
    // Перенаправление на страницу входа выполняется в компоненте
  },
  
  // Обновление профиля
  async updateProfile({ commit, state }, userData) {
    try {
      const response = await apiClient.post('/api/users/profile/', userData);
      
      const updatedUser = {
        ...state.user,
        first_name: userData.first_name,
        last_name: userData.last_name
      };
      
      localStorage.setItem('user', JSON.stringify(updatedUser));
      commit('UPDATE_USER', updatedUser);
      
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  // Удаление аккаунта
  async deleteAccount({ commit }) {
    try {
      await apiClient.delete('/api/users/delete/');
      
      commit('LOGOUT');
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
      delete axios.defaults.headers.common['Authorization'];
      
      return true;
    } catch (error) {
      throw error;
    }
  },

  // Установка PGP пароля
  setPgpPassword({ commit }, password) {
    commit('SET_PGP_PASSWORD', password);
  }
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}; 