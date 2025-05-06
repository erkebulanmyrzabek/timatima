<template>
  <div class="mail-page">
    <div class="container">
      <div class="mail-layout">
        <!-- Боковое меню -->
        <div class="mail-sidebar">
          <button 
            class="btn btn-primary btn-compose"
            @click="openComposeModal"
          >
            Написать письмо
          </button>
          
          <div class="mail-nav">
            <div 
              class="mail-nav-item" 
              :class="{ active: activeFolder === 'inbox' }"
              @click="setActiveFolder('inbox')"
            >
              <i class="fas fa-inbox"></i> Входящие
              <span class="mail-count" v-if="inboxCount > 0">{{ inboxCount }}</span>
            </div>
            
            <div 
              class="mail-nav-item" 
              :class="{ active: activeFolder === 'sent' }"
              @click="setActiveFolder('sent')"
            >
              <i class="fas fa-paper-plane"></i> Отправленные
            </div>
            
            <div 
              class="mail-nav-item" 
              :class="{ active: activeFolder === 'drafts' }"
              @click="setActiveFolder('drafts')"
            >
              <i class="fas fa-file-alt"></i> Черновики
              <span class="mail-count" v-if="draftsCount > 0">{{ draftsCount }}</span>
            </div>
            
            <div 
              class="mail-nav-item" 
              :class="{ active: activeFolder === 'trash' }"
              @click="setActiveFolder('trash')"
            >
              <i class="fas fa-trash"></i> Корзина
            </div>
          </div>
        </div>
        
        <!-- Основное содержимое -->
        <div class="mail-content">
          <!-- Выбор отображаемой папки -->
          <div v-if="loading" class="mail-loading">
            <div class="spinner"></div>
          </div>
          
          <div v-else-if="activeFolder === 'inbox'" class="mail-messages">
            <mail-message-list 
              :messages="inbox" 
              :folder="activeFolder" 
              @view-message="viewMessage"
              @delete-message="deleteMessage"
            />
          </div>
          
          <div v-else-if="activeFolder === 'sent'" class="mail-messages">
            <mail-message-list 
              :messages="sent" 
              :folder="activeFolder" 
              @view-message="viewMessage"
              @delete-message="deleteMessage"
            />
          </div>
          
          <div v-else-if="activeFolder === 'drafts'" class="mail-messages">
            <mail-message-list 
              :messages="drafts" 
              :folder="activeFolder" 
              @view-message="viewMessage"
              @delete-message="deleteMessage"
              @edit-draft="editDraft"
            />
          </div>
          
          <div v-else-if="activeFolder === 'trash'" class="mail-messages">
            <mail-message-list 
              :messages="trash" 
              :folder="activeFolder" 
              @view-message="viewMessage"
            />
          </div>
          
          <div v-else-if="activeFolder === 'view'" class="mail-message-view">
            <mail-message-view 
              :message="currentMessage" 
              @back="goBack"
              @delete="deleteOpenedMessage"
              @reply="replyToMessage"
            />
          </div>
        </div>
      </div>
    </div>
    
    <!-- Модальное окно для создания сообщения -->
    <mail-compose-modal 
      v-if="showComposeModal" 
      :draft="editingDraft"
      :reply-to="replyToData"
      @close="closeComposeModal" 
      @send="sendMessage"
      @save-draft="saveDraft"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useStore } from 'vuex';
import MailMessageList from '@/components/mail/MailMessageList.vue';
import MailMessageView from '@/components/mail/MailMessageView.vue';
import MailComposeModal from '@/components/mail/MailComposeModal.vue';

export default {
  name: 'MailPage',
  components: {
    MailMessageList,
    MailMessageView,
    MailComposeModal
  },
  setup() {
    const store = useStore();
    
    // Состояние
    const activeFolder = ref('inbox');
    const showComposeModal = ref(false);
    const currentMessage = ref(null);
    const editingDraft = ref(null);
    const replyToData = ref(null);
    
    // Загрузка данных почтовых ящиков
    const loadCurrentFolder = async () => {
      console.log('Загрузка папки:', activeFolder.value);
      
      try {
        if (activeFolder.value === 'inbox') {
          await store.dispatch('mail/fetchInbox');
          console.log('Загруженные входящие:', store.getters['mail/inbox']);
        } else if (activeFolder.value === 'sent') {
          await store.dispatch('mail/fetchSent');
          console.log('Загруженные отправленные:', store.getters['mail/sent']);
        } else if (activeFolder.value === 'drafts') {
          await store.dispatch('mail/fetchDrafts');
          console.log('Загруженные черновики:', store.getters['mail/drafts']);
        } else if (activeFolder.value === 'trash') {
          await store.dispatch('mail/fetchTrash');
          console.log('Загруженный мусор:', store.getters['mail/trash']);
        }
      } catch (error) {
        console.error('Ошибка загрузки папки:', error);
      }
    };
    
    // Загрузка входящих при монтировании
    onMounted(() => {
      console.log('Компонент MailPage загружен');
      loadCurrentFolder();
    });
    
    // Отслеживание изменения активной папки
    watch(activeFolder, () => {
      if (activeFolder.value !== 'view') {
        loadCurrentFolder();
      }
    });
    
    // Установка активной папки
    const setActiveFolder = (folder) => {
      activeFolder.value = folder;
    };
    
    // Открытие модального окна для создания сообщения
    const openComposeModal = () => {
      editingDraft.value = null;
      replyToData.value = null;
      showComposeModal.value = true;
    };
    
    // Закрытие модального окна
    const closeComposeModal = () => {
      showComposeModal.value = false;
      editingDraft.value = null;
      replyToData.value = null;
    };
    
    // Просмотр сообщения
    const viewMessage = async (messageId) => {
      try {
        await store.dispatch('mail/fetchMessage', messageId);
        currentMessage.value = store.getters['mail/currentMessage'];
        activeFolder.value = 'view';
      } catch (error) {
        console.error('Ошибка загрузки сообщения:', error);
      }
    };
    
    // Возврат к списку сообщений
    const goBack = () => {
      activeFolder.value = 'inbox';
    };
    
    // Удаление сообщения
    const deleteMessage = async (messageId) => {
      try {
        await store.dispatch('mail/deleteMessage', messageId);
        loadCurrentFolder();
      } catch (error) {
        console.error('Ошибка удаления сообщения:', error);
      }
    };
    
    // Удаление открытого сообщения
    const deleteOpenedMessage = async () => {
      if (currentMessage.value) {
        await deleteMessage(currentMessage.value.id);
        goBack();
      }
    };
    
    // Редактирование черновика
    const editDraft = (draft) => {
      editingDraft.value = draft;
      showComposeModal.value = true;
    };
    
    // Ответ на сообщение
    const replyToMessage = (message) => {
      replyToData.value = {
        to_user_id: message.from_user.id,
        subject: `Re: ${message.subject}`,
        original_content: message.content_encrypted,
        from_user: message.from_user
      };
      showComposeModal.value = true;
    };
    
    // Отправка сообщения
    const sendMessage = async (messageData) => {
      try {
        console.log('Отправка сообщения из MailPage:', messageData);
        await store.dispatch('mail/sendMessage', messageData);
        console.log('Сообщение успешно отправлено');
        closeComposeModal();
        
        // Переключаемся на папку "Отправленные" и загружаем данные
        activeFolder.value = 'sent';
        await loadCurrentFolder();
      } catch (error) {
        console.error('Ошибка отправки сообщения:', error);
      }
    };
    
    // Сохранение черновика
    const saveDraft = async (messageData) => {
      try {
        await store.dispatch('mail/saveDraft', messageData);
        closeComposeModal();
        activeFolder.value = 'drafts';
        loadCurrentFolder();
      } catch (error) {
        console.error('Ошибка сохранения черновика:', error);
      }
    };
    
    return {
      activeFolder,
      showComposeModal,
      currentMessage,
      editingDraft,
      replyToData,
      inbox: computed(() => store.getters['mail/inbox']),
      sent: computed(() => store.getters['mail/sent']),
      drafts: computed(() => store.getters['mail/drafts']),
      trash: computed(() => store.getters['mail/trash']),
      loading: computed(() => store.getters['mail/loading']),
      inboxCount: computed(() => store.getters['mail/inbox'].length),
      draftsCount: computed(() => store.getters['mail/drafts'].length),
      setActiveFolder,
      openComposeModal,
      closeComposeModal,
      viewMessage,
      goBack,
      deleteMessage,
      deleteOpenedMessage,
      editDraft,
      replyToMessage,
      sendMessage,
      saveDraft
    };
  }
}
</script>

<style scoped>
.mail-page {
  margin-bottom: 40px;
}

.mail-layout {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 30px;
  min-height: 600px;
}

.mail-sidebar {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.btn-compose {
  width: 100%;
  margin-bottom: 20px;
  padding: 10px;
}

.mail-nav {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.mail-nav-item {
  padding: 12px 15px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: background-color 0.3s;
}

.mail-nav-item i {
  margin-right: 10px;
}

.mail-nav-item:hover {
  background-color: rgba(26, 58, 52, 0.05);
}

.mail-nav-item.active {
  background-color: rgba(76, 175, 80, 0.12);
  color: var(--secondary-color);
  font-weight: 500;
}

.mail-count {
  background-color: var(--secondary-color);
  color: white;
  border-radius: 10px;
  padding: 2px 8px;
  font-size: 0.8rem;
  font-weight: 500;
}

.mail-content {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  height: 100%;
  overflow: hidden;
}

.mail-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  min-height: 400px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(76, 175, 80, 0.3);
  border-radius: 50%;
  border-top-color: var(--secondary-color);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .mail-layout {
    grid-template-columns: 1fr;
  }
  
  .mail-sidebar {
    margin-bottom: 20px;
  }
}
</style> 