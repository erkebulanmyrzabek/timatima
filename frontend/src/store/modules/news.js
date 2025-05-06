import axios from 'axios';

// Начальное состояние
const state = {
  news: [],
  featuredNews: [],
  newsItem: null,
  loading: false,
  error: null,
  totalPages: 1,
  currentPage: 1
};

// Геттеры
const getters = {
  allNews: state => state.news,
  featuredNews: state => state.featuredNews,
  newsItem: state => state.newsItem,
  loading: state => state.loading,
  error: state => state.error,
  totalPages: state => state.totalPages,
  currentPage: state => state.currentPage
};

// Мутации
const mutations = {
  SET_NEWS(state, news) {
    state.news = news;
  },
  SET_FEATURED_NEWS(state, news) {
    state.featuredNews = news;
  },
  SET_NEWS_ITEM(state, newsItem) {
    state.newsItem = newsItem;
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
  // Загрузка списка новостей
  async fetchNews({ commit }, { page = 1, limit = 10 } = {}) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get('/api/news/', {
        params: { page, limit }
      });
      
      commit('SET_NEWS', response.data.results || response.data);
      
      if (response.data.count) {
        const totalPages = Math.ceil(response.data.count / limit);
        commit('SET_PAGINATION', { totalPages, currentPage: page });
      }
      
      commit('SET_LOADING', false);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response ? error.response.data : 'Ошибка загрузки новостей');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // Загрузка новостей для главной страницы
  async fetchFeaturedNews({ commit }, { limit = 5 } = {}) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get('/api/mainpage/news/', {
        params: { limit }
      });
      
      commit('SET_FEATURED_NEWS', response.data.news || []);
      commit('SET_LOADING', false);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response ? error.response.data : 'Ошибка загрузки новостей');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // Загрузка конкретной новости
  async fetchNewsItem({ commit }, id) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get(`/api/news/${id}/`);
      commit('SET_NEWS_ITEM', response.data);
      commit('SET_LOADING', false);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response ? error.response.data : 'Ошибка загрузки новости');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // Создание новости (только для администраторов)
  async createNews({ commit, rootState }, newsData) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.post('/api/news/', newsData, {
        headers: { Authorization: `Bearer ${rootState.auth.token}` }
      });
      commit('SET_LOADING', false);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response ? error.response.data : 'Ошибка создания новости');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // Обновление новости (только для администраторов)
  async updateNews({ commit, rootState }, { id, newsData }) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.put(`/api/news/${id}/`, newsData, {
        headers: { Authorization: `Bearer ${rootState.auth.token}` }
      });
      commit('SET_LOADING', false);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response ? error.response.data : 'Ошибка обновления новости');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // Удаление новости (только для администраторов)
  async deleteNews({ commit, rootState }, id) {
    commit('SET_LOADING', true);
    try {
      await axios.delete(`/api/news/${id}/`, {
        headers: { Authorization: `Bearer ${rootState.auth.token}` }
      });
      commit('SET_LOADING', false);
      return true;
    } catch (error) {
      commit('SET_ERROR', error.response ? error.response.data : 'Ошибка удаления новости');
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