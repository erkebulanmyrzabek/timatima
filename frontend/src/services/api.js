import axios from 'axios';
import store from '@/store';

// Создаем экземпляр axios с базовой конфигурацией
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Создаем экземпляр для загрузки файлов
const uploadClient = axios.create({
  baseURL: 'http://localhost:8000',
});

// Добавляем интерцептор для запросов
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Запрос: ${config.method.toUpperCase()} ${config.baseURL}${config.url}`);
    
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    if (config.params) {
      console.log('Параметры запроса:', config.params);
    }
    
    if (config.data) {
      console.log('Данные запроса:', config.data);
    }
    
    return config;
  },
  (error) => {
    console.error('Ошибка API запроса:', error);
    return Promise.reject(error);
  }
);

// Интерцептор для запросов загрузки файлов
uploadClient.interceptors.request.use(
  (config) => {
    console.log(`Загрузка файлов: ${config.method.toUpperCase()} ${config.baseURL}${config.url}`);
    
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Не устанавливаем Content-Type, чтобы axios автоматически определил его как multipart/form-data
    
    return config;
  },
  (error) => {
    console.error('Ошибка запроса загрузки:', error);
    return Promise.reject(error);
  }
);

// Добавляем интерцептор для ответов
apiClient.interceptors.response.use(
  (response) => {
    console.log(`API Ответ ${response.status} от ${response.config.url}`, response.data);
    return response;
  },
  async (error) => {
    if (error.response) {
      console.error(`API Ошибка ${error.response.status} от ${error.config.url}`, error.response.data);
    } else {
      console.error('API Ошибка без ответа сервера:', error.message);
    }
    
    const originalRequest = error.config;
    
    // Если ошибка 401 (unauthorized) и запрос не был повторен
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Пытаемся обновить токен
        await store.dispatch('auth/refreshToken');
        
        // Если успешно, обновляем заголовок Authorization и повторяем запрос
        const token = localStorage.getItem('token');
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Если не удалось обновить токен, выходим из системы
        store.dispatch('auth/logout');
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

// Применяем тот же интерцептор ответов для uploadClient
uploadClient.interceptors.response.use(
  (response) => {
    console.log(`Загрузка файлов: Ответ ${response.status} от ${response.config.url}`, response.data);
    return response;
  },
  async (error) => {
    if (error.response) {
      console.error(`Загрузка файлов: Ошибка ${error.response.status} от ${error.config.url}`, error.response.data);
    } else {
      console.error('Загрузка файлов: Ошибка без ответа сервера:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export { uploadClient };
export default apiClient; 