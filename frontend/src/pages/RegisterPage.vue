<template>
  <div class="register-page">
    <div class="container">
      <div class="auth-form-container">
        <div class="auth-form-header">
          <h1>Регистрация</h1>
          <p>Создайте новый аккаунт, чтобы получить доступ ко всем функциям портала</p>
        </div>
        <form class="auth-form" @submit.prevent="handleSubmit">
          <div class="form-group">
            <label class="form-label" for="email">Email:</label>
            <input
              id="email"
              name="email"
              v-model="userData.email"
              type="email"
              class="form-input"
              required
              placeholder="Введите ваш email"
              autocomplete="email"
            />
          </div>
          <div class="form-group">
            <label class="form-label" for="first_name">Имя:</label>
            <input
              id="first_name"
              name="first_name"
              v-model="userData.first_name"
              type="text"
              class="form-input"
              placeholder="Введите ваше имя"
              autocomplete="given-name"
            />
          </div>
          <div class="form-group">
            <label class="form-label" for="last_name">Фамилия:</label>
            <input
              id="last_name"
              name="last_name"
              v-model="userData.last_name"
              type="text"
              class="form-input"
              placeholder="Введите вашу фамилию"
              autocomplete="family-name"
            />
          </div>
          <div class="form-group">
            <label class="form-label" for="password">Пароль:</label>
            <input
              id="password"
              name="password"
              v-model="userData.password"
              type="password"
              class="form-input"
              required
              placeholder="Введите пароль"
              autocomplete="new-password"
            />
          </div>
          <div class="form-group">
            <label class="form-label" for="confirm_password">Подтверждение пароля:</label>
            <input
              id="confirm_password"
              name="confirm_password"
              v-model="confirmPassword"
              type="password"
              class="form-input"
              required
              placeholder="Повторите пароль"
              autocomplete="new-password"
            />
            <div class="form-error" v-if="passwordError">
              {{ passwordError }}
            </div>
          </div>
          <div class="form-error" v-if="error">
            {{ error }}
          </div>
          <div class="form-actions">
            <button
              type="submit"
              class="btn btn-primary btn-block"
              :disabled="isButtonDisabled"
              :title="getButtonDisabledReason"
            >
              <span v-if="loading">Регистрация...</span>
              <span v-else>Зарегистрироваться</span>
            </button>
            <div class="button-status" v-if="isButtonDisabled">
              <small class="text-muted">
                {{ getButtonDisabledReason }}
              </small>
            </div>
          </div>
          <div class="auth-links">
            <p>Уже есть аккаунт? <router-link to="/login">Войти</router-link></p>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import * as openpgp from 'openpgp';

export default {
  name: 'RegisterPage',
  setup() {
    const store = useStore();
    const router = useRouter();

    // Данные формы
    const userData = ref({
      email: '',
      first_name: '',
      last_name: '',
      password: ''
    });

    const confirmPassword = ref('');
    const passwordError = ref('');

    // Состояние
    const loading = computed(() => store.getters['auth/loading']);
    const error = computed(() => store.getters['auth/error']);

    // Причина недоступности кнопки
    const getButtonDisabledReason = computed(() => {
      if (loading.value) return 'Выполняется регистрация...';
      if (passwordError.value) return passwordError.value;
      if (!userData.value.email) return 'Введите email';
      if (!userData.value.password) return 'Введите пароль';
      if (!confirmPassword.value) return 'Подтвердите пароль';
      return '';
    });

    const isButtonDisabled = computed(() =>
      loading.value ||
      !!passwordError.value ||
      !userData.value.email ||
      !userData.value.password ||
      !confirmPassword.value
    );

    // Валидация совпадения паролей
    watch([() => userData.value.password, confirmPassword], ([password, confirm]) => {
      if (password || confirm) {
        passwordError.value = password === confirm ? '' : 'Пароли не совпадают';
      } else {
        passwordError.value = '';
      }
    });

    // Генерация PGP ключей
    const generatePGPKeys = async (user) => {
      try {
        const pgpPassword = generateRandomPassword(16);
        store.dispatch('pgp/setPassword', pgpPassword);

        const { privateKey, publicKey } = await openpgp.generateKey({
          type: 'ecc',
          curve: 'curve25519',
          userIDs: [{
            name: `${user.first_name} ${user.last_name}`.trim() || user.email,
            email: user.email
          }],
          passphrase: pgpPassword,
          format: 'armored'
        });

        const encryptedPrivateKey = await encryptWithAES(privateKey, pgpPassword);

        const response = await fetch('http://localhost:8000/api/mail/pgp-keys/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${store.getters['auth/token']}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            public_key: publicKey,
            private_key_encrypted: encryptedPrivateKey
          })
        });

        if (response.ok) {
          const data = await response.json();
          store.dispatch('pgp/setKeys', {
            publicKey: data.public_key,
            privateKey: data.private_key_encrypted
          });
          return true;
        } else {
          return false;
        }
      } catch (error) {
        return false;
      }
    };

    // Шифрование приватного ключа с помощью AES
    const encryptWithAES = async (text, password) => {
      const encoder = new TextEncoder();
      const salt = crypto.getRandomValues(new Uint8Array(16));
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
        ['encrypt']
      );

      const iv = crypto.getRandomValues(new Uint8Array(12));
      const dataBytes = encoder.encode(text);
      const encrypted = await crypto.subtle.encrypt(
        {
          name: 'AES-GCM',
          iv
        },
        key,
        dataBytes
      );

      const encryptedArray = new Uint8Array(salt.length + iv.length + encrypted.byteLength);
      encryptedArray.set(salt, 0);
      encryptedArray.set(iv, salt.length);
      encryptedArray.set(new Uint8Array(encrypted), salt.length + iv.length);

      return btoa(String.fromCharCode.apply(null, encryptedArray));
    };

    // Генерация случайного пароля
    const generateRandomPassword = (length) => {
      const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+{}|:<>?';
      let password = '';
      for (let i = 0; i < length; i++) {
        const randomIndex = Math.floor(Math.random() * charset.length);
        password += charset[randomIndex];
      }
      return password;
    };

    // Обработка формы
    const handleSubmit = async () => {
      if (isButtonDisabled.value) return;
      try {
        await store.dispatch('auth/register', userData.value);
        await store.dispatch('auth/login', {
          email: userData.value.email,
          password: userData.value.password
        });
        await generatePGPKeys({
          email: userData.value.email,
          first_name: userData.value.first_name,
          last_name: userData.value.last_name
        });
        router.push('/');
      } catch (err) {
        // Ошибка уже обработана в хранилище и отображается через computed error
      }
    };

    return {
      userData,
      confirmPassword,
      passwordError,
      loading,
      error,
      handleSubmit,
      getButtonDisabledReason,
      isButtonDisabled
    };
  }
};
</script>

<style scoped>
.register-page {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 0;
}

.auth-form-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  max-width: 450px;
  width: 100%;
  padding: 30px;
  margin: 0 auto;
}

.auth-form-header {
  text-align: center;
  margin-bottom: 30px;
}

.auth-form-header h1 {
  font-size: 1.8rem;
  margin-bottom: 10px;
}

.auth-form-header p {
  color: var(--light-text);
}

.form-group {
  margin-bottom: 20px;
}

.btn-block {
  width: 100%;
  padding: 12px;
  font-size: 1rem;
}

.btn-block:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  background-color: #ccc;
}

.form-actions {
  margin-top: 30px;
}

.form-error {
  background-color: rgba(244, 67, 54, 0.1);
  color: var(--danger-color);
  padding: 10px;
  border-radius: 4px;
  margin-top: 5px;
}

.button-status {
  margin-top: 8px;
  text-align: center;
}

.button-status small {
  color: #666;
  font-size: 0.9em;
}

.auth-links {
  margin-top: 20px;
  text-align: center;
  color: var(--light-text);
}

.auth-links a {
  color: var(--secondary-color);
  text-decoration: none;
  font-weight: 500;
}

.auth-links a:hover {
  text-decoration: underline;
}
</style>