import apiClient from './api';

export default {
  // Поиск пользователей
  searchUsers(query) {
    return apiClient.get('/api/users/search/', { params: { query } });
  },
  
  // Получение пользователя по email
  getUserByEmail(email) {
    return apiClient.get('/api/users/by-email/', { params: { email } });
  },
  
  // Получение списка пользователей
  getUsers() {
    return apiClient.get('/api/users/');
  }
}; 