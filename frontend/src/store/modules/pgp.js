import axios from 'axios';

// Начальное состояние
const state = {
  publicKey: null,
  privateKey: null,
  password: localStorage.getItem('pgpPassword') || null,
  loading: false,
  error: null
};

// Геттеры
const getters = {
  publicKey: state => state.publicKey,
  privateKey: state => state.privateKey,
  password: state => state.password,
  loading: state => state.loading,
  error: state => state.error
};

// Мутации
const mutations = {
  SET_KEYS(state, { publicKey, privateKey }) {
    state.publicKey = publicKey;
    state.privateKey = privateKey;
  },
  SET_PASSWORD(state, password) {
    state.password = password;
    localStorage.setItem('pgpPassword', password);
  },
  SET_LOADING(state, status) {
    state.loading = status;
  },
  SET_ERROR(state, error) {
    state.error = error;
  }
};

// Действия
const actions = {
  // Загрузка ключей
  async fetchKeys({ commit, rootState }) {
    commit('SET_LOADING', true);
    try {
      const response = await axios.get('http://localhost:8000/api/mail/pgp-keys/my_keys/', {
        headers: {
          'Authorization': `Bearer ${rootState.auth.token}`,
          'Content-Type': 'application/json'
        }
      });
      
      commit('SET_KEYS', {
        publicKey: response.data.public_key,
        privateKey: response.data.private_key_encrypted
      });
      
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response ? error.response.data : 'Ошибка загрузки ключей');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Установка пароля
  setPassword({ commit }, password) {
    commit('SET_PASSWORD', password);
  }
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}; 