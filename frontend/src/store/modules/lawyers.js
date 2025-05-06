import axios from 'axios';

// Начальное состояние
const state = {
  lawyers: [],
  featuredLawyers: [],
  lawyerItem: null,
  loading: false,
  error: null,
  totalPages: 1,
  currentPage: 1
};

// Геттеры
const getters = {
  allLawyers: state => state.lawyers,
  featuredLawyers: state => state.featuredLawyers,
  lawyerItem: state => state.lawyerItem,
  loading: state => state.loading,
  error: state => state.error,
  totalPages: state => state.totalPages,
  currentPage: state => state.currentPage
};

// Мутации
const mutations = {
  SET_LAWYERS(state, lawyers) {
    state.lawyers = lawyers;
  },
  SET_FEATURED_LAWYERS(state, lawyers) {
    state.featuredLawyers = lawyers;
  },
  SET_LAWYER_ITEM(state, lawyerItem) {
    state.lawyerItem = lawyerItem;
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
  // Загрузка списка адвокатов
  async fetchLawyers({ commit }, { page = 1, limit = 10, specialization = null } = {}) {
    commit('SET_LOADING', true);
    try {
      const params = { page, limit };
      if (specialization) params.specialization = specialization;
      
      const response = await axios.get('/api/lawyers/', { params });
      
      commit('SET_LAWYERS', response.data.results || response.data);
      
      if (response.data.count) {
        const totalPages = Math.ceil(response.data.count / limit);
        commit('SET_PAGINATION', { totalPages, currentPage: page });
      }
      
      commit('SET_LOADING', false);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response ? error.response.data : 'Ошибка загрузки адвокатов');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // Загрузка избранных адвокатов для главной страницы
  async fetchFeaturedLawyers({ commit }, { limit = 6 } = {}) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get('/api/mainpage/lawyers/', {
        params: { limit, is_featured: true }
      });
      
      commit('SET_FEATURED_LAWYERS', response.data.lawyers || []);
      commit('SET_LOADING', false);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response ? error.response.data : 'Ошибка загрузки адвокатов');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // Загрузка конкретного адвоката
  async fetchLawyerItem({ commit }, id) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get(`/api/lawyers/${id}/`);
      commit('SET_LAWYER_ITEM', response.data);
      commit('SET_LOADING', false);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response ? error.response.data : 'Ошибка загрузки адвоката');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // Создание адвоката (только для администраторов)
  async createLawyer({ commit, rootState }, lawyerData) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.post('/api/lawyers/', lawyerData, {
        headers: { 
          Authorization: `Bearer ${rootState.auth.token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      commit('SET_LOADING', false);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response ? error.response.data : 'Ошибка создания адвоката');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // Обновление адвоката (только для администраторов)
  async updateLawyer({ commit, rootState }, { id, lawyerData }) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.put(`/api/lawyers/${id}/`, lawyerData, {
        headers: { 
          Authorization: `Bearer ${rootState.auth.token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      commit('SET_LOADING', false);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response ? error.response.data : 'Ошибка обновления адвоката');
      commit('SET_LOADING', false);
      throw error;
    }
  },
  
  // Удаление адвоката (только для администраторов)
  async deleteLawyer({ commit, rootState }, id) {
    commit('SET_LOADING', true);
    try {
      await axios.delete(`/api/lawyers/${id}/`, {
        headers: { Authorization: `Bearer ${rootState.auth.token}` }
      });
      commit('SET_LOADING', false);
      return true;
    } catch (error) {
      commit('SET_ERROR', error.response ? error.response.data : 'Ошибка удаления адвоката');
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