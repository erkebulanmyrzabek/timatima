<template>
  <div class="mail-message-view">
    <div class="message-header">
      <div class="message-actions">
        <button class="btn btn-outline btn-back" @click="goBack">
          &laquo; Назад
        </button>
        <div class="message-actions-right">
          <button class="btn btn-outline" @click="replyToMessage">
            <i class="fas fa-reply"></i> Ответить
          </button>
          <button class="btn btn-outline btn-delete" @click="deleteMessage">
            <i class="fas fa-trash"></i> Удалить
          </button>
        </div>
      </div>
      
      <h1 class="message-subject">{{ message.subject }}</h1>
      
      <div class="message-meta">
        <div class="message-sender">
          <span class="message-meta-label">От:</span> 
          {{ message.from_user ? message.from_user.email : 'Неизвестный отправитель' }}
        </div>
        <div class="message-recipient">
          <span class="message-meta-label">Кому:</span> 
          {{ message.to_user ? message.to_user.email : 'Неизвестный получатель' }}
        </div>
        <div class="message-date">
          <span class="message-meta-label">Дата:</span> 
          {{ formatDate(message.created_at) }}
        </div>
      </div>
    </div>
    
    <div class="message-divider"></div>
    
    <!-- Секция отображения вложений -->
    <div v-if="hasAttachments" class="message-attachments">
      <h3>
        <i class="fas fa-paperclip"></i> 
        Вложения ({{ message.attachments && message.attachments.length ? message.attachments.length : (message.attachments_meta && message.attachments_meta.length ? message.attachments_meta.length : 0) }})
      </h3>
      
      <!-- Отображение вложений из attachments (ManyToMany) -->
      <div v-if="message.attachments && message.attachments.length > 0" class="attachments-list">
        <div 
          v-for="attachment in message.attachments" 
          :key="attachment.id" 
          class="attachment-item"
        >
          <div class="attachment-icon">
            <i class="fas" :class="getFileIcon(attachment.content_type)"></i>
          </div>
          <div class="attachment-details">
            <div class="attachment-name">{{ attachment.filename }}</div>
            <div class="attachment-meta">
              {{ formatFileSize(attachment.file_size) }}
            </div>
          </div>
          <div class="attachment-actions">
            <a 
              :href="attachment.file_url" 
              :download="attachment.filename"
              class="attachment-download"
              target="_blank"
              title="Скачать файл"
              @click.prevent="downloadAttachment(attachment)"
            >
              <i class="fas fa-download"></i>
            </a>
          </div>
        </div>
      </div>
      
      <!-- Отображение вложений из meta-данных, если нет обычных вложений -->
      <div v-else-if="message.attachments_meta && message.attachments_meta.length > 0" class="attachments-list">
        <div 
          v-for="(attachment, index) in message.attachments_meta" 
          :key="index" 
          class="attachment-item"
        >
          <div class="attachment-icon">
            <i class="fas" :class="getFileIcon(attachment.type)"></i>
          </div>
          <div class="attachment-details">
            <div class="attachment-name">{{ attachment.name }}</div>
            <div class="attachment-meta">
              {{ formatFileSize(attachment.size) }}
            </div>
          </div>
          <div class="attachment-actions">
            <a 
              v-if="attachment.url"
              :href="attachment.url" 
              :download="attachment.name"
              class="attachment-download"
              target="_blank"
              title="Скачать файл"
              @click.prevent="downloadAttachment(attachment)"
            >
              <i class="fas fa-download"></i>
            </a>
          </div>
        </div>
      </div>
    </div>
    
    <div class="message-content">
      <div v-if="message.is_encrypted" class="encrypted-notice">
        <i class="fas fa-lock"></i> Вы смотрите зашифрованное сообщение
      </div>
      
      <div class="message-body">
        <!-- Если сообщение не зашифровано, показываем его содержимое -->
        <div v-if="!message.is_encrypted">
          {{ message.content_encrypted }}
        </div>
        
        <!-- Если сообщение зашифровано, показываем его расшифрованное содержимое или статус расшифровки -->
        <div v-else>
          <!-- Показываем расшифрованное содержимое -->
          <div v-if="decryptedContent" class="decrypted-content">
            {{ decryptedContent }}
          </div>
          
          <!-- Показываем индикатор процесса или ошибку расшифровки -->
          <div v-else>
            <div v-if="isDecrypting" class="decrypting-status">
              <div class="spinner"></div>
              <p>Расшифровка сообщения...</p>
            </div>
            
            <div v-else-if="decryptError" class="decrypt-error">
              <div class="decrypt-error-icon">
                <i class="fas fa-exclamation-circle"></i>
              </div>
              <div class="decrypt-error-message">
                {{ decryptError }}
              </div>
              <button 
                class="btn btn-primary btn-retry"
                @click="decryptMessage"
              >
                <i class="fas fa-sync"></i> Повторить попытку
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import * as openpgp from 'openpgp';
import { useStore } from 'vuex';

export default {
  name: 'MailMessageView',
  props: {
    message: {
      type: Object,
      required: true
    }
  },
  emits: ['back', 'delete', 'reply'],
  setup(props, { emit }) {
    const store = useStore();
    const decryptedContent = ref('');
    const decryptError = ref('');
    const isDecrypting = ref(false);
    
    // Проверяем наличие вложений
    const hasAttachments = computed(() => {
      // Проверяем массив вложений
      const hasAttachmentsArray = props.message.attachments && Array.isArray(props.message.attachments) && props.message.attachments.length > 0;
      
      // Проверяем мета-данные вложений
      const hasAttachmentsMeta = props.message.attachments_meta && Array.isArray(props.message.attachments_meta) && props.message.attachments_meta.length > 0;
      
      console.log('Данные вложений:', {
        attachments: props.message.attachments,
        attachments_meta: props.message.attachments_meta,
        hasAttachmentsArray,
        hasAttachmentsMeta
      });
      
      return hasAttachmentsArray || hasAttachmentsMeta;
    });
    
    // Определяем иконку для типа файла
    const getFileIcon = (contentType) => {
      if (!contentType) return 'fa-file';
      
      if (contentType.includes('image')) return 'fa-file-image';
      if (contentType.includes('pdf')) return 'fa-file-pdf';
      if (contentType.includes('word') || contentType.includes('document')) return 'fa-file-word';
      if (contentType.includes('excel') || contentType.includes('spreadsheet')) return 'fa-file-excel';
      if (contentType.includes('zip') || contentType.includes('rar') || contentType.includes('archive')) return 'fa-file-archive';
      if (contentType.includes('text')) return 'fa-file-alt';
      
      return 'fa-file';
    };
    
    // Форматируем размер файла
    const formatFileSize = (bytes) => {
      if (!bytes || bytes === 0) return '0 Байт';
      
      const k = 1024;
      const sizes = ['Байт', 'КБ', 'МБ', 'ГБ'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };
    
    // Форматирование даты
    const formatDate = (dateString) => {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    };
    
    // Возврат в список сообщений
    const goBack = () => {
      emit('back');
    };
    
    // Удаление сообщения
    const deleteMessage = () => {
      if (confirm('Вы уверены, что хотите удалить это сообщение?')) {
        emit('delete');
      }
    };
    
    // Ответ на сообщение
    const replyToMessage = () => {
      emit('reply', props.message);
    };
    
    // Расшифровка с AES для дополнительной защиты приватного ключа
    const decryptWithAES = async (encryptedBase64, password) => {
      try {
        // Преобразуем Base64 обратно в массив байтов
        const encryptedString = atob(encryptedBase64);
        const encryptedBytes = new Uint8Array(encryptedString.length);
        for (let i = 0; i < encryptedString.length; i++) {
          encryptedBytes[i] = encryptedString.charCodeAt(i);
        }
        
        // Извлекаем соль, вектор инициализации и зашифрованные данные
        const salt = encryptedBytes.slice(0, 16);
        const iv = encryptedBytes.slice(16, 16 + 12);
        const data = encryptedBytes.slice(16 + 12);
        
        // Генерируем ключ из пароля и соли
        const encoder = new TextEncoder();
        const passwordBytes = encoder.encode(password);
        
        const keyMaterial = await crypto.subtle.importKey(
          'raw',
          passwordBytes,
          { name: 'PBKDF2' },
          false,
          ['deriveKey']
        );
        
        const key = await crypto.subtle.deriveKey(
          {
            name: 'PBKDF2',
            salt,
            iterations: 100000,
            hash: 'SHA-256'
          },
          keyMaterial,
          { name: 'AES-GCM', length: 256 },
          false,
          ['decrypt']
        );
        
        // Расшифровываем данные
        const decrypted = await crypto.subtle.decrypt(
          {
            name: 'AES-GCM',
            iv
          },
          key,
          data
        );
        
        // Преобразуем расшифрованные данные обратно в строку
        const decoder = new TextDecoder();
        return decoder.decode(decrypted);
      } catch (error) {
        console.error('Ошибка расшифровки AES:', error);
        throw new Error('Не удалось расшифровать приватный ключ: ' + error.message);
      }
    };
    
    // Расшифровка PGP сообщения
    const decryptMessage = async () => {
      isDecrypting.value = true;
      decryptError.value = '';
      
      try {
        // Получаем пароль из хранилища
        const pgpPassword = store.getters['pgp/password'];
        
        if (!pgpPassword) {
          decryptError.value = 'Пароль PGP не найден. Пожалуйста, установите пароль в настройках профиля.';
          return;
        }

        console.log('Начинаем процесс расшифровки...');
        console.log('Пароль получен:', pgpPassword ? 'Да' : 'Нет');

        // Загружаем ключи из хранилища
        await store.dispatch('pgp/fetchKeys');
        const encryptedPrivateKey = store.getters['pgp/privateKey'];
        
        console.log('Зашифрованный приватный ключ получен:', encryptedPrivateKey ? 'Да' : 'Нет');
        console.log('Зашифрованное сообщение:', props.message.content_encrypted);
        
        if (!encryptedPrivateKey) {
          decryptError.value = 'Не удалось загрузить приватный ключ. Проверьте наличие ключа в профиле.';
          return;
        }
        
        // Расшифровываем дополнительное шифрование AES
        console.log('Расшифровываем дополнительное шифрование...');
        const pgpPrivateKey = await decryptWithAES(encryptedPrivateKey, pgpPassword);
        console.log('Расшифрован PGP-приватный ключ:', pgpPrivateKey ? 'Да' : 'Нет');
        
        // Расшифровываем сообщение с помощью PGP ключа
        try {
          console.log('Читаем зашифрованный приватный ключ...');
          // Читаем приватный ключ (он уже зашифрован паролем PGP)
          const privateKeyObj = await openpgp.readPrivateKey({
            armoredKey: pgpPrivateKey
          });
          console.log('Приватный ключ прочитан успешно');
          
          console.log('Расшифровываем ключ с помощью пароля...');
          // Расшифровываем ключ с помощью пароля пользователя
          const decryptedPrivateKey = await openpgp.decryptKey({
            privateKey: privateKeyObj,
            passphrase: pgpPassword
          });
          console.log('Ключ расшифрован успешно');
          
          console.log('Читаем зашифрованное сообщение...');
          // Читаем зашифрованное сообщение
          const encryptedMessage = await openpgp.readMessage({
            armoredMessage: props.message.content_encrypted
          });
          console.log('Сообщение прочитано успешно');
          
          console.log('Расшифровываем сообщение...');
          // Расшифровываем сообщение с помощью расшифрованного приватного ключа
          const { data: decrypted } = await openpgp.decrypt({
            message: encryptedMessage,
            decryptionKeys: decryptedPrivateKey
          });
          console.log('Сообщение расшифровано успешно');
          
          // Показываем расшифрованное сообщение
          decryptedContent.value = decrypted;
        } catch (error) {
          console.error('Ошибка расшифровки:', error);
          if (error.message.includes('passphrase')) {
            decryptError.value = 'Неверный пароль для расшифровки ключа';
          } else if (error.message.includes('No decryption key packets found')) {
            decryptError.value = 'Не удалось найти ключ для расшифровки. Возможно, сообщение зашифровано другим ключом.';
          } else {
            decryptError.value = 'Не удалось расшифровать сообщение: ' + error.message;
          }
        }
      } catch (error) {
        console.error('Ошибка загрузки ключа:', error);
        decryptError.value = 'Ошибка загрузки ключа: ' + error.message;
      } finally {
        isDecrypting.value = false;
      }
    };
    
    // Автоматически запускаем расшифровку при изменении сообщения, если оно зашифровано
    watch(() => props.message, (newMessage) => {
      console.log('Сообщение обновлено:', newMessage);
      console.log('Вложения:', newMessage.attachments);
      console.log('Мета вложений:', newMessage.attachments_meta);
      
      if (newMessage && newMessage.is_encrypted && !decryptedContent.value) {
        console.log('Автоматическая расшифровка сообщения...');
        decryptMessage();
      }
    }, { immediate: true, deep: true });
    
    // При монтировании компонента проверяем вложения и запускаем расшифровку
    onMounted(() => {
      console.log('Компонент MailMessageView смонтирован');
      console.log('Сообщение:', props.message);
      console.log('Вложения:', props.message.attachments);
      console.log('Мета вложений:', props.message.attachments_meta);
      
      if (props.message && props.message.is_encrypted && !decryptedContent.value) {
        console.log('Автоматическая расшифровка сообщения...');
        decryptMessage();
      }
    });
    
    // В блоке script добавляем функцию downloadAttachment
    const downloadAttachment = (attachment) => {
      // Создаем невидимый элемент ссылки для программного скачивания
      const link = document.createElement('a');
      
      // Проверяем тип вложения (обычное или из metadata)
      const isMetaAttachment = !attachment.file_url && attachment.url;
      
      // Используем соответствующие поля в зависимости от типа вложения
      link.href = isMetaAttachment ? attachment.url : attachment.file_url;
      link.download = isMetaAttachment ? attachment.name : attachment.filename;
      link.target = '_blank';
      
      // Добавляем ссылку в DOM и активируем клик
      document.body.appendChild(link);
      link.click();
      
      // Удаляем ссылку из DOM
      setTimeout(() => {
        document.body.removeChild(link);
      }, 100);
    };
    
    return {
      decryptedContent,
      decryptError,
      isDecrypting,
      hasAttachments,
      formatDate,
      goBack,
      deleteMessage,
      replyToMessage,
      decryptMessage,
      getFileIcon,
      formatFileSize,
      downloadAttachment
    };
  }
}
</script>

<style scoped>
.mail-message-view {
  height: 100%;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.message-header {
  margin-bottom: 20px;
}

.message-actions {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.message-actions-right {
  display: flex;
  gap: 10px;
}

.btn-back {
  padding: 8px 16px;
}

.btn-delete {
  color: var(--danger-color);
  border-color: var(--danger-color);
}

.btn-delete:hover {
  background-color: var(--danger-color);
  color: white;
}

.message-subject {
  font-size: 1.5rem;
  margin-bottom: 15px;
}

.message-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 10px;
  color: var(--light-text);
  font-size: 0.95rem;
}

.message-meta-label {
  font-weight: 600;
  color: var(--primary-color);
}

.message-divider {
  height: 1px;
  background-color: var(--border-color);
  margin: 20px 0;
}

.message-content {
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  flex-grow: 1;
}

.encrypted-notice {
  background-color: rgba(76, 175, 80, 0.1);
  padding: 10px 15px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
  color: var(--secondary-color);
  font-weight: 500;
}

.message-body {
  font-size: 1rem;
  line-height: 1.6;
}

.decrypted-content {
  padding: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background-color: #fff;
  white-space: pre-wrap;
}

.decrypting-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.decrypt-error {
  background-color: #ffebee;
  padding: 1.5rem;
  border-radius: 4px;
  margin: 1rem 0;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.decrypt-error-icon {
  font-size: 2rem;
  color: #e53935;
}

.decrypt-error-message {
  color: #c62828;
  margin-bottom: 1rem;
}

.btn-retry {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-retry:hover {
  background-color: #43a047;
}

/* Стили для вложений */
.message-attachments {
  margin-bottom: 20px;
}

.message-attachments h3 {
  font-size: 1.1rem;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--dark-text);
}

.attachments-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
}

.attachment-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: white;
  transition: all 0.2s ease;
}

.attachment-item:hover {
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.08);
}

.attachment-icon {
  font-size: 1.8rem;
  margin-right: 15px;
  color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
}

.attachment-details {
  flex-grow: 1;
  overflow: hidden;
}

.attachment-name {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 3px;
}

.attachment-meta {
  font-size: 0.8rem;
  color: var(--light-text);
}

.attachment-actions {
  display: flex;
  align-items: center;
}

.attachment-download {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  color: var(--primary-color);
  text-decoration: none;
  transition: background-color 0.2s ease;
}

.attachment-download:hover {
  background-color: rgba(var(--primary-color-rgb), 0.1);
}

.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid rgba(76, 175, 80, 0.3);
  border-radius: 50%;
  border-top-color: #4caf50;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .attachments-list {
    grid-template-columns: 1fr;
  }
  
  .message-meta {
    grid-template-columns: 1fr;
  }
  
  .message-actions {
    flex-direction: column;
    gap: 10px;
  }
  
  .message-actions-right {
    width: 100%;
    justify-content: space-between;
  }
}
</style> 