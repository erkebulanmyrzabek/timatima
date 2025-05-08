<template>
  <div class="profile-page">
    <div class="container">
      <div class="profile-header">
        <h1>Профиль пользователя</h1>
      </div>
      
      <div class="profile-content">
        <div class="profile-card">
          <div class="profile-info">
            <h2>Личная информация</h2>
            
            <div v-if="loading" class="loading-spinner">
              <div class="spinner"></div>
            </div>
            
            <form v-else @submit.prevent="updateProfile" class="profile-form">
              <div class="form-group">
                <label class="form-label" for="email">Email:</label>
                <input 
                  id="email" 
                  type="email" 
                  v-model="userProfile.email" 
                  class="form-input" 
                  disabled
                />
              </div>
              
              <div class="form-group">
                <label class="form-label" for="first_name">Имя:</label>
                <input 
                  id="first_name" 
                  type="text" 
                  v-model="userProfile.first_name" 
                  class="form-input" 
                  placeholder="Введите ваше имя"
                />
              </div>
              
              <div class="form-group">
                <label class="form-label" for="last_name">Фамилия:</label>
                <input 
                  id="last_name" 
                  type="text" 
                  v-model="userProfile.last_name" 
                  class="form-input" 
                  placeholder="Введите вашу фамилию"
                />
              </div>
              
              <div class="form-error" v-if="error">
                {{ error }}
              </div>
              
              <div class="form-actions">
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  Сохранить изменения
                </button>
              </div>
            </form>
          </div>
        </div>
        
        <!-- Секция для PGP ключей -->
        <div class="profile-card">
          <div class="pgp-keys-section">
            <h2>PGP Ключи для шифрования писем</h2>
            
            <div v-if="pgpLoading" class="loading-spinner">
              <div class="spinner"></div>
            </div>
            
            <div v-else>
              <div v-if="hasPgpKeys" class="pgp-keys-info">
                <div class="pgp-status">
                  <i class="fas fa-lock text-success"></i> 
                  <span>У вас настроены PGP ключи для безопасной переписки</span>
                </div>
                <div class="form-group">
                  <label class="form-label" for="public_key">Публичный ключ:</label>
                  <textarea 
                    id="public_key" 
                    v-model="pgpKeyData.public_key" 
                    class="form-input form-textarea" 
                    rows="4"
                    readonly
                  ></textarea>
                </div>
                <div class="pgp-actions">
                  <button 
                    @click="regenerateKeys" 
                    class="btn btn-outline"
                    :disabled="pgpGenerating"
                  >
                    <i class="fas fa-sync-alt"></i> 
                    {{ pgpGenerating ? 'Генерация ключей...' : 'Сгенерировать новые ключи' }}
                  </button>
                </div>
              </div>
              
              <div v-else class="pgp-setup">
                <p>
                  Для безопасной переписки необходимо настроить PGP ключи.
                  Вы можете сгенерировать новую пару ключей или указать существующие.
                </p>
                
                <div class="pgp-options">
                  <button 
                    @click="generateNewKeys" 
                    class="btn btn-primary"
                    :disabled="pgpGenerating"
                  >
                    <i class="fas fa-key"></i> 
                    {{ pgpGenerating ? 'Генерация ключей...' : 'Сгенерировать ключи' }}
                  </button>
                  
                  <button 
                    @click="showManualKeyInput = !showManualKeyInput" 
                    class="btn btn-outline"
                  >
                    <i class="fas fa-edit"></i> Указать свои ключи
                  </button>
                </div>
                
                <form v-if="showManualKeyInput" @submit.prevent="savePgpKeys" class="pgp-manual-form">
                  <div class="form-group">
                    <label class="form-label" for="manual_public_key">Публичный ключ:</label>
                    <textarea 
                      id="manual_public_key" 
                      v-model="pgpKeyData.public_key" 
                      class="form-input form-textarea" 
                      rows="4"
                      placeholder="-----BEGIN PGP PUBLIC KEY BLOCK-----"
                      required
                    ></textarea>
                  </div>
                  
                  <div class="form-group">
                    <label class="form-label" for="manual_private_key">Приватный ключ (будет зашифрован):</label>
                    <textarea 
                      id="manual_private_key" 
                      v-model="pgpKeyData.private_key" 
                      class="form-input form-textarea" 
                      rows="4"
                      placeholder="-----BEGIN PGP PRIVATE KEY BLOCK-----"
                      required
                    ></textarea>
                  </div>
                  
                  <div class="form-group">
                    <label class="form-label" for="key_password">Пароль для шифрования приватного ключа:</label>
                    <input 
                      id="key_password" 
                      type="password" 
                      v-model="pgpKeyPassword" 
                      class="form-input" 
                      placeholder="Минимум 8 символов"
                      required
                      minlength="8"
                    />
                  </div>
                  
                  <div class="form-error" v-if="pgpError">
                    {{ pgpError }}
                  </div>
                  
                  <div class="form-actions">
                    <button type="submit" class="btn btn-primary" :disabled="pgpSaving">
                      {{ pgpSaving ? 'Сохранение...' : 'Сохранить ключи' }}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
        
        <div class="profile-card">
          <div class="password-change">
            <h2>Изменение пароля</h2>
            
            <form @submit.prevent="changePassword" class="password-form">
              <div class="form-group">
                <label class="form-label" for="current_password">Текущий пароль:</label>
                <input 
                  id="current_password" 
                  type="password" 
                  v-model="passwordData.current_password" 
                  class="form-input" 
                  required
                />
              </div>
              
              <div class="form-group">
                <label class="form-label" for="new_password">Новый пароль:</label>
                <input 
                  id="new_password" 
                  type="password" 
                  v-model="passwordData.new_password" 
                  class="form-input" 
                  required
                />
              </div>
              
              <div class="form-group">
                <label class="form-label" for="confirm_password">Подтверждение нового пароля:</label>
                <input 
                  id="confirm_password" 
                  type="password" 
                  v-model="passwordData.confirm_password" 
                  class="form-input" 
                  required
                />
              </div>
              
              <div class="form-error" v-if="passwordError">
                {{ passwordError }}
              </div>
              
              <div class="form-actions">
                <button type="submit" class="btn btn-primary" :disabled="passwordLoading">
                  Изменить пароль
                </button>
              </div>
            </form>
          </div>
        </div>
        
        <div class="profile-card danger-zone">
          <h2>Опасная зона</h2>
          <p>Внимание! Эти действия необратимы:</p>
          
          <button 
            class="btn btn-danger" 
            @click="confirmDeleteAccount"
          >
            Удалить аккаунт
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import * as openpgp from 'openpgp';

export default {
  name: 'ProfilePage',
  setup() {
    const store = useStore();
    const router = useRouter();
    
    // Данные пользователя
    const userProfile = ref({
      email: '',
      first_name: '',
      last_name: ''
    });
    
    // Данные для PGP ключей
    const pgpKeyData = ref({
      public_key: '',
      private_key: '',
      private_key_encrypted: ''
    });
    const pgpKeyPassword = ref('');
    const hasPgpKeys = ref(false);
    const pgpLoading = ref(false);
    const pgpGenerating = ref(false);
    const pgpSaving = ref(false);
    const pgpError = ref('');
    const showManualKeyInput = ref(false);
    
    // Данные для смены пароля
    const passwordData = ref({
      current_password: '',
      new_password: '',
      confirm_password: ''
    });
    
    // Состояние
    const loading = computed(() => store.getters['auth/loading']);
    const error = computed(() => store.getters['auth/error']);
    const passwordLoading = ref(false);
    const passwordError = ref('');
    
    // Загрузка данных пользователя
    onMounted(async () => {
      const user = store.getters['auth/user'];
      if (user) {
        userProfile.value = {
          email: user.email || '',
          first_name: user.first_name || '',
          last_name: user.last_name || ''
        };
        
        // Загружаем PGP ключи
        await loadPgpKeys();
      } else {
        // Если пользователь не загружен, перенаправляем на страницу входа
        router.push('/login');
      }
    });
    
    // Обновление профиля
    const updateProfile = async () => {
      try {
        await store.dispatch('auth/updateProfile', {
          first_name: userProfile.value.first_name,
          last_name: userProfile.value.last_name
        });
        
        alert('Профиль успешно обновлен');
      } catch (err) {
        console.error('Ошибка обновления профиля:', err);
      }
    };
    
    // Загрузка PGP ключей
    const loadPgpKeys = async () => {
      pgpLoading.value = true;
      pgpError.value = '';
      
      try {
        const response = await fetch('http://localhost:8000/api/mail/pgp-keys/my_keys/', {
          method: 'GET',
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          pgpKeyData.value.public_key = data.public_key;
          pgpKeyData.value.private_key_encrypted = data.private_key_encrypted;
          hasPgpKeys.value = true;
        } else if (response.status === 404) {
          // Ключи не найдены, нормальная ситуация
          hasPgpKeys.value = false;
        } else {
          // Другая ошибка
          const errorData = await response.json();
          pgpError.value = errorData.detail || 'Ошибка загрузки ключей';
        }
      } catch (err) {
        console.error('Ошибка загрузки PGP ключей:', err);
        pgpError.value = 'Ошибка загрузки ключей. Проверьте соединение.';
      } finally {
        pgpLoading.value = false;
      }
    };
    
    // Генерация новой пары ключей
    const generateNewKeys = async () => {
      pgpGenerating.value = true;
      pgpError.value = '';
      
      try {
        // Генерируем случайный пароль, если пользователь не указал
        if (!pgpKeyPassword.value) {
          pgpKeyPassword.value = generateRandomPassword(16);
        }
        
        // Сохраняем пароль в хранилище
        store.dispatch('pgp/setPassword', pgpKeyPassword.value);
        
        console.log('Генерируем пару ключей с помощью OpenPGP.js...');
        // Генерируем пару ключей с помощью OpenPGP.js
        const { privateKey, publicKey } = await openpgp.generateKey({
          type: 'ecc', // тип: ECC (более современный и быстрый)
          curve: 'curve25519', // кривая для ECC
          userIDs: [{ name: userProfile.value.first_name + ' ' + userProfile.value.last_name, email: userProfile.value.email }],
          passphrase: pgpKeyPassword.value,
          format: 'armored' // экспортируем в текстовом формате (ASCII armored)
        });
        
        console.log('Ключи сгенерированы успешно');
        
        // Сохраняем сгенерированные ключи
        pgpKeyData.value.public_key = publicKey;
        pgpKeyData.value.private_key = privateKey; // Приватный ключ уже зашифрован паролем
        
        // Сохраняем ключи на сервере
        await savePgpKeys();
      } catch (err) {
        console.error('Ошибка генерации PGP ключей:', err);
        pgpError.value = 'Ошибка генерации ключей: ' + err.message;
      } finally {
        pgpGenerating.value = false;
      }
    };
    
    // Регенерация ключей (для существующих пользователей)
    const regenerateKeys = async () => {
      const confirm = window.confirm('Вы уверены, что хотите сгенерировать новые ключи? Все зашифрованные письма больше не будут доступны для чтения.');
      if (confirm) {
        // Сбрасываем состояние и генерируем новые ключи
        hasPgpKeys.value = false;
        pgpKeyData.value = {
          public_key: '',
          private_key: '',
          private_key_encrypted: ''
        };
        pgpKeyPassword.value = '';
        await generateNewKeys();
      }
    };
    
    // Сохранение PGP ключей
    const savePgpKeys = async () => {
      pgpSaving.value = true;
      pgpError.value = '';
      
      try {
        console.log('Начинаем сохранение PGP ключей...');
        
        // Проверяем наличие ключей
        if (!pgpKeyData.value.public_key || !pgpKeyData.value.private_key) {
          throw new Error('Отсутствуют необходимые ключи');
        }
        
        console.log('Публичный ключ:', pgpKeyData.value.public_key.substring(0, 50) + '...');
        console.log('Приватный ключ (зашифрованный PGP):', pgpKeyData.value.private_key.substring(0, 50) + '...');
        
        // Дополнительно шифруем приватный ключ (который уже зашифрован PGP) 
        // перед отправкой на сервер для дополнительной защиты
        const additionalEncryptedPrivateKey = await encryptWithAES(
          pgpKeyData.value.private_key, 
          pgpKeyPassword.value
        );
        
        console.log('Приватный ключ с дополнительным шифрованием')
        
        // Отправляем дополнительно зашифрованный приватный ключ
        const response = await fetch('http://localhost:8000/api/mail/pgp-keys/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${store.getters['auth/token']}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            public_key: pgpKeyData.value.public_key,
            private_key_encrypted: additionalEncryptedPrivateKey // Дополнительно зашифрованный ключ
          })
        });
        
        if (response.ok) {
          const data = await response.json();
          console.log('Ключи успешно сохранены:', data);
          
          // Обновляем данные в компоненте
          pgpKeyData.value.public_key = data.public_key;
          pgpKeyData.value.private_key_encrypted = data.private_key_encrypted;
          
          // Сохраняем также зашифрованную копию приватного ключа в хранилище
          store.dispatch('pgp/setKeys', {
            publicKey: data.public_key,
            privateKey: data.private_key_encrypted
          });
          
          hasPgpKeys.value = true;
          showManualKeyInput.value = false;
          
          alert('PGP ключи успешно сохранены. Запомните ваш пароль для шифрования!');
        } else {
          const errorData = await response.json();
          console.error('Ошибка сохранения ключей:', errorData);
          pgpError.value = errorData.detail || 'Ошибка сохранения ключей';
        }
      } catch (err) {
        console.error('Ошибка сохранения PGP ключей:', err);
        pgpError.value = 'Ошибка сохранения ключей: ' + err.message;
      } finally {
        pgpSaving.value = false;
      }
    };
    
    // Шифрование с AES для дополнительной защиты приватного ключа
    const encryptWithAES = async (text, password) => {
      // Создаем соль и ключ на основе пароля
      const encoder = new TextEncoder();
      const salt = crypto.getRandomValues(new Uint8Array(16));
      const passwordBytes = encoder.encode(password);
      
      // Генерируем ключ из пароля и соли
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
        ['encrypt']
      );
      
      // Создаем вектор инициализации
      const iv = crypto.getRandomValues(new Uint8Array(12));
      
      // Шифруем данные
      const dataBytes = encoder.encode(text);
      const encrypted = await crypto.subtle.encrypt(
        {
          name: 'AES-GCM',
          iv
        },
        key,
        dataBytes
      );
      
      // Объединяем соль, вектор инициализации и зашифрованные данные
      const encryptedArray = new Uint8Array(salt.length + iv.length + encrypted.byteLength);
      encryptedArray.set(salt, 0);
      encryptedArray.set(iv, salt.length);
      encryptedArray.set(new Uint8Array(encrypted), salt.length + iv.length);
      
      // Преобразуем в Base64
      return btoa(String.fromCharCode.apply(null, encryptedArray));
    };
    
    // Изменение пароля
    const changePassword = async () => {
      passwordError.value = '';
      
      // Проверка совпадения паролей
      if (passwordData.value.new_password !== passwordData.value.confirm_password) {
        passwordError.value = 'Пароли не совпадают';
        return;
      }
      
      passwordLoading.value = true;
      
      try {
        // В реальном проекте здесь будет вызов API для смены пароля
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Очистка формы
        passwordData.value = {
          current_password: '',
          new_password: '',
          confirm_password: ''
        };
        
        alert('Пароль успешно изменен');
      } catch (err) {
        passwordError.value = 'Ошибка при изменении пароля';
        console.error('Ошибка изменения пароля:', err);
      } finally {
        passwordLoading.value = false;
      }
    };
    
    // Подтверждение удаления аккаунта
    const confirmDeleteAccount = () => {
      if (confirm('Вы уверены, что хотите удалить свой аккаунт? Это действие невозможно отменить.')) {
        deleteAccount();
      }
    };
    
    // Удаление аккаунта
    const deleteAccount = async () => {
      try {
        await store.dispatch('auth/deleteAccount');
        router.push('/');
      } catch (err) {
        console.error('Ошибка удаления аккаунта:', err);
        alert('Произошла ошибка при удалении аккаунта. Попробуйте позже.');
      }
    };
    
    // Вспомогательная функция для генерации случайного пароля
    const generateRandomPassword = (length) => {
      const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+{}|:<>?';
      let password = '';
      for (let i = 0; i < length; i++) {
        const randomIndex = Math.floor(Math.random() * charset.length);
        password += charset[randomIndex];
      }
      return password;
    };
    
    return {
      userProfile,
      passwordData,
      pgpKeyData,
      pgpKeyPassword,
      hasPgpKeys,
      pgpLoading,
      pgpGenerating,
      pgpSaving,
      pgpError,
      showManualKeyInput,
      loading,
      error,
      passwordLoading,
      passwordError,
      updateProfile,
      changePassword,
      confirmDeleteAccount,
      generateNewKeys,
      regenerateKeys,
      savePgpKeys
    };
  }
};
</script>

<style scoped>
.profile-page {
  padding: 2rem 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.profile-header {
  margin-bottom: 2rem;
  text-align: center;
}

.profile-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

.profile-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-textarea {
  min-height: 100px;
  font-family: monospace;
  font-size: 0.85rem;
}

.form-actions {
  margin-top: 2rem;
}

.form-error {
  color: #e53935;
  margin-top: 0.5rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn-primary {
  background-color: #1976d2;
  color: white;
}

.btn-primary:hover {
  background-color: #1565c0;
}

.btn-outline {
  background-color: transparent;
  border: 1px solid #1976d2;
  color: #1976d2;
}

.btn-outline:hover {
  background-color: #f5f5f5;
}

.btn-danger {
  background-color: #e53935;
  color: white;
}

.btn-danger:hover {
  background-color: #d32f2f;
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.danger-zone {
  border-top: 2px solid #ffebee;
  padding-top: 1.5rem;
}

.loading-spinner {
  display: flex;
  justify-content: center;
  padding: 2rem 0;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top: 4px solid #1976d2;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Стили для PGP секции */
.pgp-keys-section h2 {
  margin-bottom: 1.5rem;
}

.pgp-status {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
  padding: 0.75rem;
  background-color: #e8f5e9;
  border-radius: 4px;
}

.pgp-status i {
  color: #43a047;
  margin-right: 0.75rem;
  font-size: 1.25rem;
}

.pgp-options {
  display: flex;
  gap: 1rem;
  margin: 1.5rem 0;
}

.pgp-manual-form {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
}

.pgp-actions {
  margin-top: 1.5rem;
}

.text-success {
  color: #43a047;
}

@media (min-width: 768px) {
  .profile-content {
    grid-template-columns: 1fr;
  }
}
</style> 