<template>
  <div class="mail-message-list">
    <div class="mail-list-header">
      <h2>{{ folderTitle }}</h2>
      <div class="mail-list-actions">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Поиск..." 
          class="mail-search" 
        />
      </div>
    </div>
    
    <div class="mail-list-content">
      <div v-if="filteredMessages.length === 0" class="mail-empty">
        <p>{{ emptyMessage }}</p>
      </div>
      
      <div v-else class="mail-list">
        <div 
          v-for="message in filteredMessages" 
          :key="message.id" 
          class="mail-list-item"
          @click="viewMessage(message.id)"
        >
          <div class="mail-item-content">
            <div class="mail-sender">
              {{ getSenderName(message) }}
            </div>
            <div class="mail-subject">
              {{ message.subject }}
              <span v-if="message.has_attachments" class="attachment-indicator" title="Содержит вложения">
                <i class="fas fa-paperclip"></i>
              </span>
            </div>
            <div class="mail-date">
              {{ formatDate(message.created_at) }}
            </div>
          </div>
          
          <div class="mail-item-actions">
            <button 
              v-if="folder === 'drafts'" 
              class="mail-action-btn" 
              @click.stop="editDraft(message)"
              title="Редактировать черновик"
            >
              <i class="fas fa-edit"></i>
            </button>
            
            <button 
              v-if="folder !== 'trash'" 
              class="mail-action-btn" 
              @click.stop="deleteMessage(message.id)"
              title="Удалить сообщение"
            >
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';

export default {
  name: 'MailMessageList',
  props: {
    messages: {
      type: Array,
      default: () => []
    },
    folder: {
      type: String,
      required: true
    }
  },
  emits: ['view-message', 'delete-message', 'edit-draft'],
  setup(props, { emit }) {
    const searchQuery = ref('');
    
    // Фильтрация сообщений
    const filteredMessages = computed(() => {
      if (!searchQuery.value) return props.messages;
      
      const query = searchQuery.value.toLowerCase();
      return props.messages.filter(message => {
        const senderName = getSenderName(message).toLowerCase();
        const subject = message.subject.toLowerCase();
        
        return senderName.includes(query) || subject.includes(query);
      });
    });
    
    // Получение названия папки
    const folderTitle = computed(() => {
      switch (props.folder) {
        case 'inbox': return 'Входящие';
        case 'sent': return 'Отправленные';
        case 'drafts': return 'Черновики';
        case 'trash': return 'Корзина';
        default: return 'Сообщения';
      }
    });
    
    // Сообщение при отсутствии писем
    const emptyMessage = computed(() => {
      switch (props.folder) {
        case 'inbox': return 'Нет входящих сообщений';
        case 'sent': return 'Нет отправленных сообщений';
        case 'drafts': return 'Нет черновиков';
        case 'trash': return 'Корзина пуста';
        default: return 'Нет сообщений';
      }
    });
    
    // Получение имени отправителя/получателя
    const getSenderName = (message) => {
      console.log('Данные сообщения для отображения:', message);
      
      if (!message) {
        return 'Неизвестный пользователь';
      }
      
      if (props.folder === 'inbox' && message.from_user) {
        const fromUser = message.from_user;
        // Показываем имя, если есть, иначе email
        if (fromUser.first_name || fromUser.last_name) {
          return `${fromUser.first_name || ''} ${fromUser.last_name || ''}`.trim();
        }
        return fromUser.email || 'Неизвестный отправитель';
      } else if (message.to_user) {
        const toUser = message.to_user;
        // Показываем имя, если есть, иначе email
        if (toUser.first_name || toUser.last_name) {
          return `${toUser.first_name || ''} ${toUser.last_name || ''}`.trim();
        }
        return toUser.email || 'Неизвестный получатель';
      }
      
      // Запасной вариант, если данных нет
      return props.folder === 'inbox' ? 'Неизвестный отправитель' : 'Неизвестный получатель';
    };
    
    // Форматирование даты
    const formatDate = (dateString) => {
      const date = new Date(dateString);
      const today = new Date();
      
      // Если сообщение от сегодня, показываем только время
      if (date.toDateString() === today.toDateString()) {
        return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
      }
      
      // Иначе показываем дату
      return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
    };
    
    // Просмотр сообщения
    const viewMessage = (id) => {
      emit('view-message', id);
    };
    
    // Удаление сообщения
    const deleteMessage = (id) => {
      emit('delete-message', id);
    };
    
    // Редактирование черновика
    const editDraft = (draft) => {
      emit('edit-draft', draft);
    };
    
    return {
      searchQuery,
      filteredMessages,
      folderTitle,
      emptyMessage,
      getSenderName,
      formatDate,
      viewMessage,
      deleteMessage,
      editDraft
    };
  }
}
</script>

<style scoped>
.mail-message-list {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.mail-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
}

.mail-list-header h2 {
  margin: 0;
  font-size: 1.5rem;
}

.mail-search {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  width: 200px;
}

.mail-list-content {
  flex-grow: 1;
  overflow-y: auto;
}

.mail-empty {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: var(--light-text);
}

.mail-list-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background-color 0.3s;
}

.mail-list-item:hover {
  background-color: rgba(0, 0, 0, 0.03);
}

.mail-item-content {
  flex-grow: 1;
  display: grid;
  grid-template-columns: 250px 1fr 150px;
  gap: 15px;
  align-items: center;
}

.mail-sender {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mail-subject {
  color: var(--dark-text);
  font-weight: 500;
  flex-grow: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: flex;
  align-items: center;
  gap: 5px;
}

.attachment-indicator {
  color: var(--light-text);
  font-size: 0.85rem;
}

.mail-date {
  text-align: right;
  color: var(--lighter-text);
  font-size: 0.9rem;
}

.mail-item-actions {
  display: flex;
  gap: 10px;
  opacity: 0;
  transition: opacity 0.3s;
}

.mail-list-item:hover .mail-item-actions {
  opacity: 1;
}

.mail-action-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--light-text);
  padding: 5px;
  transition: color 0.3s;
}

.mail-action-btn:hover {
  color: var(--primary-color);
}

@media (max-width: 768px) {
  .mail-item-content {
    grid-template-columns: 1fr;
    gap: 5px;
  }
  
  .mail-sender, .mail-subject {
    font-size: 0.9rem;
  }
  
  .mail-date {
    text-align: left;
    margin-top: 5px;
  }
  
  .mail-item-actions {
    opacity: 1;
  }
}
</style> 