import { uploadClient } from './api';

/**
 * Сервис для работы с файлами
 */
const filesService = {
  /**
   * Загрузить файлы на сервер
   * 
   * @param {FormData} formData - FormData с файлами
   * @returns {Promise} - Промис с ответом сервера
   */
  uploadAttachments(formData) {
    return uploadClient.post('/api/mail/attachments/upload_multiple/', formData);
  },
  
  /**
   * Получить файл по его ID
   * 
   * @param {string} fileId - ID файла
   * @returns {Promise} - Промис с ответом сервера
   */
  getAttachment(fileId) {
    return uploadClient.get(`/api/mail/attachments/${fileId}/`);
  },
  
  /**
   * Удалить файл по его ID
   * 
   * @param {string} fileId - ID файла
   * @returns {Promise} - Промис с ответом сервера
   */
  deleteAttachment(fileId) {
    return uploadClient.delete(`/api/mail/attachments/${fileId}/`);
  }
};

export default filesService; 