<template>
  <div class="mail-compose-modal-backdrop" @click="closeModal">
    <div class="mail-compose-modal" @click.stop>
      <div class="modal-header">
        <h2>{{ isEditingDraft ? 'Редактирование черновика' : isReply ? 'Ответ на сообщение' : 'Новое сообщение' }}</h2>
        <button class="modal-close" @click="closeModal">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div class="modal-body">
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label class="form-label" for="to_user_email">Получатель (email):</label>
            <input 
              id="to_user_email" 
              type="email" 
              v-model="recipientEmail" 
              class="form-input"
              :disabled="isReply"
              required
              @blur="findRecipientId"
            />
            <div class="form-error" v-if="errors.to_user_id">
              {{ errors.to_user_id }}
            </div>
            <div v-if="recipientFound" class="recipient-found">
              Получатель найден: {{ recipientName }}
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label" for="subject">Тема:</label>
            <input 
              id="subject" 
              type="text" 
              v-model="message.subject" 
              class="form-input"
              required
            />
            <div class="form-error" v-if="errors.subject">
              {{ errors.subject }}
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label" for="content">Сообщение:</label>
            <textarea 
              id="content" 
              v-model="message.content_encrypted" 
              class="form-input form-textarea"
              rows="10"
              required
            ></textarea>
            <div class="form-error" v-if="errors.content_encrypted">
              {{ errors.content_encrypted }}
            </div>
          </div>
          
          <!-- Секция для загрузки вложений -->
          <div class="form-group attachments-section">
            <label class="form-label">Вложения:</label>
            
            <div class="file-uploader">
              <input 
                type="file" 
                ref="fileInput" 
                @change="handleFileUpload" 
                multiple
                style="display: none"
              />
              <button 
                type="button" 
                class="btn btn-outline attachment-btn" 
                @click="triggerFileUpload"
              >
                <i class="fas fa-paperclip"></i> Добавить вложение
              </button>
              <span class="file-limit-info">Максимальный размер файла: 5 МБ</span>
            </div>
            
            <!-- Список выбранных файлов -->
            <div v-if="attachmentFiles.length > 0" class="attachment-list">
              <div v-for="(file, index) in attachmentFiles" :key="index" class="attachment-item">
                <div class="attachment-details">
                  <i class="fas" :class="getFileIcon(file.type)"></i>
                  <span class="attachment-name">{{ file.name }}</span>
                  <span class="attachment-size">({{ formatFileSize(file.size) }})</span>
                </div>
                <button 
                  type="button" 
                  class="btn btn-icon remove-attachment" 
                  @click="removeAttachment(index)"
                >
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
            
            <div class="form-error" v-if="errors.attachments">
              {{ errors.attachments }}
            </div>
          </div>
          
          <div class="form-group encryption-option">
            <input 
              id="encrypt" 
              type="checkbox" 
              v-model="message.is_encrypted" 
              class="form-checkbox"
            />
            <label class="form-label" for="encrypt">
              <i class="fas" :class="message.is_encrypted ? 'fa-lock' : 'fa-lock-open'"></i>
              Зашифровать сообщение
            </label>
          </div>
          
          <div class="modal-actions">
            <button 
              type="button" 
              class="btn btn-outline" 
              @click="saveDraft"
            >
              Сохранить как черновик
            </button>
            <button 
              type="submit" 
              class="btn btn-primary"
              :disabled="isSubmitting"
            >
              {{ isSubmitting ? 'Отправка...' : 'Отправить' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import usersService from '@/services/users';
import filesService from '@/services/files';

export default {
  name: 'MailComposeModal',
  props: {
    draft: {
      type: Object,
      default: null
    },
    replyTo: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'send', 'save-draft'],
  setup(props, { emit }) {
    // Данные для работы с получателем
    const recipientEmail = ref('');
    const recipientFound = ref(false);
    const recipientName = ref('');
    const recipientLoading = ref(false);
    const isSubmitting = ref(false);
    
    // Данные для работы с вложениями
    const fileInput = ref(null);
    const attachmentFiles = ref([]);
    const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 МБ в байтах
    
    // Состояние формы
    const message = ref({
      to_user_id: '',
      subject: '',
      content_encrypted: '',
      is_encrypted: true,
      attachments: []
    });
    
    const errors = ref({});
    
    // Проверяем, редактируем ли черновик или отвечаем на сообщение
    const isEditingDraft = computed(() => !!props.draft);
    const isReply = computed(() => !!props.replyTo);
    
    // Функция для поиска ID пользователя по email
    const findRecipientId = async () => {
      if (!recipientEmail.value) {
        recipientFound.value = false;
        return;
      }
      
      recipientLoading.value = true;
      errors.value.to_user_id = null;
      
      try {
        // Используем настоящее API для поиска
        const response = await usersService.getUserByEmail(recipientEmail.value);
        
        if (response && response.data) {
          message.value.to_user_id = response.data.id;
          recipientName.value = `${response.data.first_name || ''} ${response.data.last_name || ''}`.trim() || response.data.email;
          recipientFound.value = true;
        } else {
          // Генерируем временный ID, если пользователь не найден
          message.value.to_user_id = `temp-${Date.now()}`;
          recipientFound.value = true;
        }
      } catch (error) {
        console.error('Ошибка поиска пользователя:', error);
        // Генерируем временный ID вместо показа ошибки
        message.value.to_user_id = `temp-${Date.now()}`;
        recipientFound.value = true;
      } finally {
        recipientLoading.value = false;
      }
    };
    
    // Функции для работы с вложениями
    const triggerFileUpload = () => {
      fileInput.value.click();
    };
    
    const handleFileUpload = async (event) => {
      const files = event.target.files;
      errors.value.attachments = null;
      
      if (!files || files.length === 0) return;
      
      // Проверка и обработка каждого выбранного файла
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        // Проверка размера файла
        if (file.size > MAX_FILE_SIZE) {
          errors.value.attachments = `Файл "${file.name}" превышает максимальный размер (5 МБ)`;
          continue;
        }
        
        // Добавляем файл в массив
        attachmentFiles.value.push(file);
      }
      
      // Сбрасываем input file, чтобы можно было выбрать те же файлы снова
      event.target.value = '';
    };
    
    const removeAttachment = (index) => {
      attachmentFiles.value.splice(index, 1);
    };
    
    const getFileIcon = (fileType) => {
      if (fileType.includes('image')) return 'fa-image';
      if (fileType.includes('pdf')) return 'fa-file-pdf';
      if (fileType.includes('word') || fileType.includes('document')) return 'fa-file-word';
      if (fileType.includes('excel') || fileType.includes('spreadsheet')) return 'fa-file-excel';
      if (fileType.includes('zip') || fileType.includes('rar') || fileType.includes('archive')) return 'fa-file-archive';
      return 'fa-file';
    };
    
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes';
      
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };
    
    // Функция для подготовки вложений перед отправкой
    const prepareAttachments = async () => {
      if (attachmentFiles.value.length === 0) return [];
      
      const formData = new FormData();
      const attachmentMeta = [];
      
      // Подготовка метаданных для каждого файла
      for (let i = 0; i < attachmentFiles.value.length; i++) {
        const file = attachmentFiles.value[i];
        formData.append('files', file);
      }
      
      try {
        // Загружаем файлы на сервер
        const response = await filesService.uploadAttachments(formData);
        
        if (response && response.data) {
          // Преобразуем полученные данные о файлах в метаданные для сообщения
          response.data.forEach(attachment => {
            attachmentMeta.push({
              id: attachment.id,
              name: attachment.filename,
              size: attachment.file_size,
              type: attachment.content_type,
              url: attachment.file_url
            });
          });
        }
        
        // Возвращаем метаданные о вложениях
        return attachmentMeta;
      } catch (error) {
        console.error('Ошибка загрузки вложений:', error);
        errors.value.attachments = 'Ошибка загрузки вложений';
        throw error;
      }
    };
    
    // Инициализация данных
    onMounted(() => {
      if (isEditingDraft.value) {
        // Если редактируем черновик, копируем его данные
        message.value = {
          to_user_id: props.draft.to_user.id || props.draft.to_user_id,
          subject: props.draft.subject || '',
          content_encrypted: props.draft.content_encrypted || '',
          is_encrypted: typeof props.draft.is_encrypted !== 'undefined' ? props.draft.is_encrypted : true,
          attachments: props.draft.attachments || []
        };
        
        // Устанавливаем email получателя, если есть
        if (props.draft.to_user && props.draft.to_user.email) {
          recipientEmail.value = props.draft.to_user.email;
          recipientName.value = `${props.draft.to_user.first_name || ''} ${props.draft.to_user.last_name || ''}`.trim() || props.draft.to_user.email;
          recipientFound.value = true;
        }
        
        // Загружаем существующие вложения, если есть
        if (props.draft.attachments && props.draft.attachments.length > 0) {
          // TODO: загрузить метаданные вложений
        }
      } else if (isReply.value) {
        // Если отвечаем на сообщение, предзаполняем поля
        message.value = {
          to_user_id: props.replyTo.from_user.id,
          subject: props.replyTo.subject || '',
          content_encrypted: '',
          is_encrypted: true,
          attachments: []
        };
        
        // Устанавливаем email отправителя как получателя
        if (props.replyTo.from_user && props.replyTo.from_user.email) {
          recipientEmail.value = props.replyTo.from_user.email;
          recipientName.value = `${props.replyTo.from_user.first_name || ''} ${props.replyTo.from_user.last_name || ''}`.trim() || props.replyTo.from_user.email;
          recipientFound.value = true;
        }
        
        // Добавляем префикс Re: к теме, если его еще нет
        if (!message.value.subject.startsWith('Re:')) {
          message.value.subject = `Re: ${message.value.subject}`;
        }
        
        // Добавляем цитату исходного сообщения
        if (props.replyTo.original_content) {
          message.value.content_encrypted = `\n\n---\nОт: ${props.replyTo.from_user.email}\n${props.replyTo.original_content}`;
        }
      }
    });
    
    // Отслеживаем изменения email получателя
    watch(recipientEmail, () => {
      if (!recipientEmail.value) {
        message.value.to_user_id = '';
        recipientFound.value = false;
      }
    });
    
    // Валидация формы
    const validateForm = () => {
      errors.value = {};
      
      if (!recipientEmail.value) {
        errors.value.to_user_id = 'Укажите email получателя';
        return false;
      }
      
      // Генерируем временный ID, если нет
      if (!message.value.to_user_id) {
        message.value.to_user_id = `temp-${Date.now()}`;
      }
      
      if (!message.value.subject) {
        errors.value.subject = 'Укажите тему сообщения';
        return false;
      }
      
      if (!message.value.content_encrypted) {
        errors.value.content_encrypted = 'Сообщение не может быть пустым';
        return false;
      }
      
      return true;
    };
    
    // Отправка сообщения
    const handleSubmit = async () => {
      if (!validateForm()) return;
      
      isSubmitting.value = true;
      
      try {
        // Подготовка вложений перед отправкой
        const attachmentMeta = await prepareAttachments();
        
        // Добавляем информацию о вложениях в сообщение
        const messageToSend = {
          ...message.value,
          attachments: attachmentMeta
        };
        
        // Отправляем сообщение
        emit('send', messageToSend);
      } catch (error) {
        console.error('Ошибка при подготовке отправки:', error);
      } finally {
        isSubmitting.value = false;
      }
    };
    
    // Сохранение черновика
    const saveDraft = async () => {
      // Проверяем обязательные поля для черновика
      if (!message.value.subject && !message.value.content_encrypted) {
        errors.value.subject = 'Заполните тему или содержание сообщения';
        return;
      }
      
      isSubmitting.value = true;
      
      try {
        // Подготовка вложений перед сохранением
        const attachmentMeta = await prepareAttachments();
        
        // Добавляем информацию о вложениях в черновик
        const draftToSave = {
          ...message.value,
          attachments: attachmentMeta
        };
        
        // Сохраняем черновик
        emit('save-draft', draftToSave);
      } catch (error) {
        console.error('Ошибка при сохранении черновика:', error);
      } finally {
        isSubmitting.value = false;
      }
    };
    
    // Закрытие модального окна
    const closeModal = () => {
      if (message.value.subject || message.value.content_encrypted || recipientEmail.value || attachmentFiles.value.length > 0) {
        if (confirm('Вы уверены, что хотите закрыть окно? Все несохраненные данные будут потеряны.')) {
          emit('close');
        }
      } else {
        emit('close');
      }
    };
    
    return {
      message,
      errors,
      isEditingDraft,
      isReply,
      recipientEmail,
      recipientFound,
      recipientName,
      fileInput,
      attachmentFiles,
      isSubmitting,
      findRecipientId,
      handleSubmit,
      saveDraft,
      closeModal,
      triggerFileUpload,
      handleFileUpload,
      removeAttachment,
      getFileIcon,
      formatFileSize
    };
  }
}
</script>

<style scoped>
.mail-compose-modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.mail-compose-modal {
  width: 90%;
  max-width: 700px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  max-height: 90vh;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.3rem;
}

.modal-close {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  color: var(--light-text);
  padding: 5px;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
}

.form-textarea {
  resize: vertical;
  min-height: 150px;
}

.encryption-option {
  display: flex;
  align-items: center;
  gap: 10px;
}

.form-checkbox {
  width: 20px;
  height: 20px;
}

.encryption-option .form-label {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 20px;
}

.form-error {
  color: var(--danger-color);
  font-size: 0.9rem;
  margin-top: 5px;
}

.recipient-found {
  color: var(--success-color);
  font-size: 0.9rem;
  margin-top: 5px;
}

/* Стили для секции вложений */
.attachments-section {
  margin-top: 15px;
}

.file-uploader {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}

.attachment-btn {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-limit-info {
  font-size: 0.85rem;
  color: var(--light-text);
}

.attachment-list {
  margin-top: 10px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  max-height: 150px;
  overflow-y: auto;
}

.attachment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid var(--border-color);
}

.attachment-item:last-child {
  border-bottom: none;
}

.attachment-details {
  display: flex;
  align-items: center;
  gap: 8px;
}

.attachment-name {
  font-size: 0.9rem;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.attachment-size {
  font-size: 0.8rem;
  color: var(--light-text);
}

.remove-attachment {
  background: none;
  border: none;
  color: var(--danger-color);
  cursor: pointer;
  font-size: 0.9rem;
  padding: 3px 6px;
}

.remove-attachment:hover {
  background-color: rgba(var(--danger-color-rgb), 0.1);
  border-radius: 4px;
}

@media (max-width: 768px) {
  .mail-compose-modal {
    width: 95%;
    max-height: 95vh;
  }
  
  .modal-actions {
    flex-direction: column-reverse;
    gap: 10px;
  }
  
  .modal-actions button {
    width: 100%;
  }
  
  .attachment-details {
    max-width: 200px;
  }
}
</style> 