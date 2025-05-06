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
    
    <!-- Отладочная информация о вложениях -->
    <div class="debug-info">
      <p>has_attachments: {{ hasAttachments }}</p>
      <p>attachments: {{ JSON.stringify(message.attachments) || '[]' }}</p>
      <p>attachments_meta: {{ JSON.stringify(message.attachments_meta) || '[]' }}</p>
      <p>Длина attachments: {{ message.attachments ? message.attachments.length : 0 }}</p>
      <p>Длина attachments_meta: {{ message.attachments_meta ? message.attachments_meta.length : 0 }}</p>
    </div>
    
    <!-- Секция отображения вложений -->
    <div v-if="hasAttachments" class="message-attachments">
      <h3>
        <i class="fas fa-paperclip"></i> 
        Вложения ({{ message.attachments ? message.attachments.length : 0 }})
      </h3>
      <div class="attachments-list">
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
              download
              class="attachment-download"
              target="_blank"
              title="Скачать файл"
            >
              <i class="fas fa-download"></i>
            </a>
          </div>
        </div>
      </div>
      
      <!-- Отображение вложений из meta-данных, если нет обычных вложений -->
      <div v-if="message.attachments.length === 0 && message.attachments_meta && message.attachments_meta.length > 0">
        <h4>Мета-данные вложений:</h4>
        <div class="attachments-list">
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
                download
                class="attachment-download"
                target="_blank"
                title="Скачать файл"
              >
                <i class="fas fa-download"></i>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="message-content">
      <div v-if="message.is_encrypted" class="encrypted-notice">
        <i class="fas fa-lock"></i> Это сообщение зашифровано
      </div>
      
      <div class="message-body">
        <!-- Отображаем содержимое письма -->
        <div v-if="!message.is_encrypted">
          {{ message.content_encrypted }}
        </div>
        <div v-else>
          <div class="encrypted-content">
            {{ decryptedContent || 'Содержимое сообщения зашифровано' }}
          </div>
          <button 
            v-if="!decryptedContent" 
            class="btn btn-primary btn-decrypt"
            @click="decryptMessage"
          >
            Расшифровать сообщение
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';

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
    const decryptedContent = ref('');
    
    // Проверяем наличие вложений
    const hasAttachments = computed(() => {
      // Проверяем массив вложений
      const hasAttachmentsArray = props.message.attachments && props.message.attachments.length > 0;
      
      // Проверяем мета-данные вложений
      const hasAttachmentsMeta = props.message.attachments_meta && props.message.attachments_meta.length > 0;
      
      console.log('Данные вложений:', {
        attachments: props.message.attachments,
        attachments_meta: props.message.attachments_meta,
        hasAttachmentsArray,
        hasAttachmentsMeta
      });
      
      return hasAttachmentsArray || hasAttachmentsMeta;
    });
    
    // Отслеживаем изменения в props.message для обновления состояния
    watch(() => props.message, (newMessage) => {
      console.log('Сообщение обновлено:', newMessage);
      console.log('Вложения:', newMessage.attachments);
      console.log('Мета вложений:', newMessage.attachments_meta);
    }, { deep: true });
    
    // При монтировании компонента проверяем вложения
    onMounted(() => {
      console.log('Компонент MailMessageView смонтирован');
      console.log('Сообщение:', props.message);
      console.log('Вложения:', props.message.attachments);
      console.log('Мета вложений:', props.message.attachments_meta);
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
    
    // Эмуляция расшифровки сообщения
    const decryptMessage = () => {
      // В реальном приложении здесь должна быть логика расшифровки
      decryptedContent.value = props.message.content_encrypted || 
        'Содержимое этого сообщения было успешно расшифровано.';
    };
    
    return {
      decryptedContent,
      hasAttachments,
      formatDate,
      goBack,
      deleteMessage,
      replyToMessage,
      decryptMessage,
      getFileIcon,
      formatFileSize
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

.encrypted-content {
  margin-bottom: 20px;
}

.btn-decrypt {
  margin-top: 15px;
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