import apiClient from './api';

/**
 * Сервис для работы с почтовыми сообщениями
 */
const mailService = {
  /**
   * Получить список всех сообщений
   * 
   * @returns {Promise} - Промис с ответом сервера
   */
  getMessages() {
    return apiClient.get('/api/mail/');
  },
  
  /**
   * Получить входящие сообщения
   * 
   * @returns {Promise} - Промис с ответом сервера
   */
  getInbox() {
    return apiClient.get('/api/mail/inbox/');
  },
  
  /**
   * Получить отправленные сообщения
   * 
   * @returns {Promise} - Промис с ответом сервера
   */
  getSent() {
    return apiClient.get('/api/mail/sent/');
  },
  
  /**
   * Получить черновики
   * 
   * @returns {Promise} - Промис с ответом сервера
   */
  getDrafts() {
    return apiClient.get('/api/mail/drafts/');
  },
  
  /**
   * Получить удаленные сообщения
   * 
   * @returns {Promise} - Промис с ответом сервера
   */
  getTrash() {
    return apiClient.get('/api/mail/trash/');
  },
  
  /**
   * Получить сообщение по ID
   * 
   * @param {string} id - ID сообщения
   * @returns {Promise} - Промис с ответом сервера
   */
  getMessage(id) {
    return apiClient.get(`/api/mail/${id}/`);
  },
  
  /**
   * Отправить новое сообщение
   * 
   * @param {Object} messageData - Данные сообщения
   * @returns {Promise} - Промис с ответом сервера
   */
  sendMessage(messageData) {
    console.log('Отправка сообщения:', messageData);
    return apiClient.post('/api/mail/', messageData);
  },
  
  /**
   * Обновить сообщение
   * 
   * @param {string} id - ID сообщения
   * @param {Object} messageData - Данные сообщения
   * @returns {Promise} - Промис с ответом сервера
   */
  updateMessage(id, messageData) {
    return apiClient.put(`/api/mail/${id}/`, messageData);
  },
  
  /**
   * Удалить сообщение (в корзину)
   * 
   * @param {string} id - ID сообщения
   * @returns {Promise} - Промис с ответом сервера
   */
  deleteMessage(id) {
    return apiClient.delete(`/api/mail/${id}/`);
  },
  
  /**
   * Восстановить сообщение из корзины
   * 
   * @param {string} id - ID сообщения
   * @returns {Promise} - Промис с ответом сервера
   */
  restoreMessage(id) {
    return apiClient.post(`/api/mail/${id}/restore/`);
  },
  
  /**
   * Полностью удалить сообщение (из корзины)
   * 
   * @param {string} id - ID сообщения
   * @returns {Promise} - Промис с ответом сервера
   */
  permanentDeleteMessage(id) {
    return apiClient.post(`/api/mail/${id}/permanent_delete/`);
  }
};

export default mailService; 