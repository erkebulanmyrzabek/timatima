import axios from 'axios';
import apiClient from '@/services/api';

// Начальное состояние
const state = {
  inbox: [],
  sent: [],
  drafts: [],
  trash: [],
  currentMessage: null,
  loading: false,
  error: null,
  totalPages: 1,
  currentPage: 1
};

// Геттеры
const getters = {
  inbox: state => state.inbox,
  sent: state => state.sent,
  drafts: state => state.drafts,
  trash: state => state.trash,
  currentMessage: state => state.currentMessage,
  loading: state => state.loading,
  error: state => state.error,
  totalPages: state => state.totalPages,
  currentPage: state => state.currentPage
};

// Мутации
const mutations = {
  SET_INBOX(state, messages) {
    state.inbox = messages;
  },
  SET_SENT(state, messages) {
    state.sent = messages;
  },
  SET_DRAFTS(state, messages) {
    state.drafts = messages;
  },
  SET_TRASH(state, messages) {
    state.trash = messages;
  },
  SET_CURRENT_MESSAGE(state, message) {
    state.currentMessage = message;
  },
  SET_LOADING(state, status) {
    state.loading = status;
  },
  SET_ERROR(state, error) {
    state.error = error;
  },
  SET_PAGINATION(state, { totalPages, currentPage }) {
    state.totalPages = totalPages;
    state.currentPage = currentPage;
  }
};

// Действия
const actions = {
  // Загрузка входящих сообщений
  async fetchInbox({ commit }, { page = 1, limit = 10 } = {}) {
    commit('SET_LOADING', true);
    try {
      console.log('Запрос входящих писем:', '/api/mail/inbox/');
      const response = await apiClient.get('/api/mail/inbox/', {
        params: { page, limit }
      });
      
      console.log('Ответ входящих писем:', response.data);
      
      // Проверяем структуру данных и корректно обрабатываем ответ
      if (Array.isArray(response.data)) {
        // Если ответ - прямой массив
        commit('SET_INBOX', response.data);
        const totalPages = Math.ceil(response.data.length / limit);
        commit('SET_PAGINATION', { totalPages, currentPage: page });
      } else if (response.data.messages) {
        // Если ответ содержит объект с полем messages
        commit('SET_INBOX', response.data.messages || []);
        if (response.data.total) {
          const totalPages = Math.ceil(response.data.total / limit);
          commit('SET_PAGINATION', { totalPages, currentPage: page });
        }
      } else if (response.data.results && Array.isArray(response.data.results)) {
        // Если ответ в формате с пагинацией Django REST Framework
        commit('SET_INBOX', response.data.results);
        if (response.data.count) {
          const totalPages = Math.ceil(response.data.count / limit);
          commit('SET_PAGINATION', { totalPages, currentPage: page });
        }
      } else {
        // Если ничего не подошло, просто устанавливаем пустой массив
        commit('SET_INBOX', []);
      }
      
      commit('SET_LOADING', false);
      return response.data;
    } catch (error) {
      console.error('Ошибка загрузки входящих писем:', error);
      commit('SET_ERROR', error.response ? error.response.data : 'Ошибка загрузки входящих сообщений');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // Загрузка отправленных сообщений
  async fetchSent({ commit }, { page = 1, limit = 10 } = {}) {
    commit('SET_LOADING', true);
    try {
      console.log('Запрос отправленных писем:', '/api/mail/sent/');
      const response = await apiClient.get('/api/mail/sent/', {
        params: { page, limit }
      });
      
      console.log('Ответ отправленных писем:', response.data);
      
      // Проверяем структуру данных и корректно обрабатываем ответ
      if (Array.isArray(response.data)) {
        // Если ответ - прямой массив
        commit('SET_SENT', response.data);
        const totalPages = Math.ceil(response.data.length / limit);
        commit('SET_PAGINATION', { totalPages, currentPage: page });
      } else if (response.data.messages) {
        // Если ответ содержит объект с полем messages
        commit('SET_SENT', response.data.messages || []);
        if (response.data.total) {
          const totalPages = Math.ceil(response.data.total / limit);
          commit('SET_PAGINATION', { totalPages, currentPage: page });
        }
      } else if (response.data.results && Array.isArray(response.data.results)) {
        // Если ответ в формате с пагинацией Django REST Framework
        commit('SET_SENT', response.data.results);
        if (response.data.count) {
          const totalPages = Math.ceil(response.data.count / limit);
          commit('SET_PAGINATION', { totalPages, currentPage: page });
        }
      } else {
        // Если ничего не подошло, просто устанавливаем пустой массив
        commit('SET_SENT', []);
      }
      
      commit('SET_LOADING', false);
      return response.data;
    } catch (error) {
      console.error('Ошибка загрузки отправленных писем:', error);
      commit('SET_ERROR', error.response ? error.response.data : 'Ошибка загрузки отправленных сообщений');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // Загрузка черновиков
  async fetchDrafts({ commit }, { page = 1, limit = 10 } = {}) {
    commit('SET_LOADING', true);
    try {
      const response = await apiClient.get('/api/mail/drafts/', {
        params: { page, limit }
      });
      
      commit('SET_DRAFTS', response.data.messages || []);
      
      if (response.data.total) {
        const totalPages = Math.ceil(response.data.total / limit);
        commit('SET_PAGINATION', { totalPages, currentPage: page });
      }
      
      commit('SET_LOADING', false);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response ? error.response.data : 'Ошибка загрузки черновиков');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // Загрузка удаленных сообщений
  async fetchTrash({ commit }, { page = 1, limit = 10 } = {}) {
    commit('SET_LOADING', true);
    try {
      const response = await apiClient.get('/api/mail/trash/', {
        params: { page, limit }
      });
      
      commit('SET_TRASH', response.data.messages || []);
      
      if (response.data.total) {
        const totalPages = Math.ceil(response.data.total / limit);
        commit('SET_PAGINATION', { totalPages, currentPage: page });
      }
      
      commit('SET_LOADING', false);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response ? error.response.data : 'Ошибка загрузки удаленных сообщений');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // Загрузка отдельного сообщения
  async fetchMessage({ commit }, id) {
    commit('SET_LOADING', true);
    try {
      console.log('Запрос сообщения по ID:', `/api/mail/${id}/`);
      const response = await apiClient.get(`/api/mail/${id}/`);
      
      console.log('Ответ по сообщению (полные данные):', response.data);
      
      // Если в ответе нет массива attachments, создаем его
      if (!response.data.attachments) {
        response.data.attachments = [];
      }
      
      // Проверяем attachments_meta
      console.log('Проверка attachments_meta:', response.data.attachments_meta);
      
      // Если attachments_meta отсутствует или null, устанавливаем пустой массив
      if (!response.data.attachments_meta) {
        response.data.attachments_meta = [];
      }
      
      // Дополнительная проверка: если есть attachments_meta но attachments пустой, 
      // подготавливаем attachments на основе attachments_meta
      if (response.data.attachments.length === 0 && 
          response.data.attachments_meta && 
          response.data.attachments_meta.length > 0) {
        console.log('Есть мета-данные вложений, но массив вложений пуст. Преобразовываем...');
        
        // Копируем данные из attachments_meta в attachments для отображения
        response.data.attachments = response.data.attachments_meta.map(meta => ({
          id: meta.id,
          filename: meta.name,
          file_size: meta.size,
          content_type: meta.type,
          file_url: meta.url,
          created_at: new Date().toISOString() // Добавляем текущую дату, так как её нет в мета-данных
        }));
        
        console.log('Преобразованные вложения:', response.data.attachments);
      }
      
      commit('SET_CURRENT_MESSAGE', response.data);
      commit('SET_LOADING', false);
      return response.data;
    } catch (error) {
      console.error('Ошибка загрузки сообщения:', error);
      commit('SET_ERROR', error.response ? error.response.data : 'Ошибка загрузки сообщения');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // Отправка нового сообщения
  async sendMessage({ commit, dispatch }, messageData) {
    commit('SET_LOADING', true);
    try {
      // Устанавливаем is_draft = false для отправки
      const data = { ...messageData, is_draft: false };
      
      console.log('Отправка сообщения:', data);
      const response = await apiClient.post('/api/mail/', data);
      
      console.log('Ответ после отправки:', response.data);
      // Обновляем отправленные сообщения после успешной отправки
      await dispatch('fetchSent');
      
      commit('SET_LOADING', false);
      return response.data;
    } catch (error) {
      console.error('Ошибка отправки сообщения:', error);
      commit('SET_ERROR', error.response ? error.response.data : 'Ошибка отправки сообщения');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // Сохранение черновика
  async saveDraft({ commit }, messageData) {
    commit('SET_LOADING', true);
    try {
      // Устанавливаем is_draft = true для сохранения как черновик
      const data = { ...messageData, is_draft: true };
      
      const response = await apiClient.post('/api/mail/', data);
      
      commit('SET_LOADING', false);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response ? error.response.data : 'Ошибка сохранения черновика');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // Удаление сообщения (перемещение в корзину)
  async deleteMessage({ commit }, id) {
    commit('SET_LOADING', true);
    try {
      await apiClient.delete(`/api/mail/${id}/`);
      
      commit('SET_LOADING', false);
      return true;
    } catch (error) {
      commit('SET_ERROR', error.response ? error.response.data : 'Ошибка удаления сообщения');
      commit('SET_LOADING', false);
      throw error;
    }
  }
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}; 