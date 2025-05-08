import axios from 'axios';

// Начальное состояние
const state = {
  publicKey: null,
  privateKey: null, // Хранит зашифрованный приватный ключ
  password: localStorage.getItem('pgpPassword') || null, // Пароль для расшифровки
  decryptedPrivateKey: null, // Временное хранение расшифрованного ключа в памяти
  loading: false,
  error: null
};

// Геттеры
const getters = {
  publicKey: state => state.publicKey,
  privateKey: state => state.privateKey,
  password: state => state.password,
  decryptedPrivateKey: state => state.decryptedPrivateKey,
  loading: state => state.loading,
  error: state => state.error
};

// Мутации
const mutations = {
  SET_KEYS(state, { publicKey, privateKey }) {
    state.publicKey = publicKey;
    state.privateKey = privateKey;
  },
  SET_DECRYPTED_KEY(state, decryptedKey) {
    // Храним расшифрованный ключ только в памяти (не в localStorage)
    state.decryptedPrivateKey = decryptedKey;
  },
  SET_PASSWORD(state, password) {
    state.password = password;
    localStorage.setItem('pgpPassword', password);
  },
  CLEAR_DECRYPTED_KEY(state) {
    state.decryptedPrivateKey = null;
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
      
      console.log('Ключи получены с сервера:', {
        publicKey: response.data.public_key ? 'Да' : 'Нет',
        privateKey: response.data.private_key_encrypted ? 'Да' : 'Нет'
      });
      
      commit('SET_KEYS', {
        publicKey: response.data.public_key,
        privateKey: response.data.private_key_encrypted
      });
      
      return response.data;
    } catch (error) {
      console.error('Ошибка при загрузке ключей:', error);
      commit('SET_ERROR', error.response ? error.response.data : 'Ошибка загрузки ключей');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Установка ключей напрямую (используется при генерации)
  setKeys({ commit }, { publicKey, privateKey }) {
    commit('SET_KEYS', { publicKey, privateKey });
  },
  
  // Установка пароля
  setPassword({ commit }, password) {
    commit('SET_PASSWORD', password);
  },
  
  // Сохранение расшифрованного ключа
  setDecryptedKey({ commit }, decryptedKey) {
    commit('SET_DECRYPTED_KEY', decryptedKey);
  },
  
  // Очистка расшифрованного ключа (вызывается при выходе из системы)
  clearDecryptedKey({ commit }) {
    commit('CLEAR_DECRYPTED_KEY');
  },
  
  // Очистка всех ключей при выходе
  clearAllKeys({ commit }) {
    commit('SET_KEYS', { publicKey: null, privateKey: null });
    commit('CLEAR_DECRYPTED_KEY');
  }
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}; 