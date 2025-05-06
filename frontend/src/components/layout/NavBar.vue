<template>
  <div class="navbar">
    <div class="container navbar-content">
      <div class="navbar-logo">
        <router-link to="/">
          <div class="logo-wrapper">
            <img src="@/assets/images/logo.svg" alt="Дом Адвокатов" />
            <span>DOM ADVOKATOV</span>
          </div>
        </router-link>
      </div>
      <div class="navbar-links">
        <router-link to="/news" class="nav-link">Новости</router-link>
        <router-link to="/mail" class="nav-link">Почта</router-link>
        <router-link to="/documents" class="nav-link">Документы</router-link>
        <router-link to="/lawyers" class="nav-link">Адвокаты</router-link>
        <router-link to="/podcasts" class="nav-link">Подкасты</router-link>
      </div>
      <div class="navbar-auth">
        <select v-model="selectedLanguage" class="lang-selector">
          <option value="ru">Рус</option>
          <option value="kz">Каз</option>
          <option value="en">Eng</option>
        </select>
        <div v-if="!isAuthenticated">
          <router-link to="/login" class="btn btn-login">Войти в аккаунт</router-link>
        </div>
        <div v-else class="user-menu">
          <div class="user-info" @click="toggleUserMenu">
            <span>{{ user.email }}</span>
            <div v-if="isUserMenuOpen" class="user-dropdown">
              <router-link to="/profile" class="dropdown-item">Профиль</router-link>
              <router-link to="/my-documents" class="dropdown-item">Мои документы</router-link>
              <div class="dropdown-item" @click="logout">Выйти</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'NavBar',
  data() {
    return {
      isUserMenuOpen: false,
      selectedLanguage: 'ru'
    }
  },
  computed: {
    ...mapGetters('auth', ['isAuthenticated', 'user'])
  },
  methods: {
    ...mapActions('auth', ['logout']),
    toggleUserMenu() {
      this.isUserMenuOpen = !this.isUserMenuOpen;
    }
  },
  watch: {
    selectedLanguage(newVal) {
      console.log('Язык изменен на:', newVal);
      // Здесь добавить логику смены языка
    }
  }
}
</script>

<style scoped>
.navbar {
  background-color: #1a3a34;
  color: white;
  padding: 15px 0;
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-wrapper {
  display: flex;
  align-items: center;
  color: white;
  text-decoration: none;
}

.logo-wrapper img {
  height: 30px;
  margin-right: 10px;
}

.navbar-links {
  display: flex;
  gap: 20px;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

.nav-link:hover {
  color: #4caf50;
}

.navbar-auth {
  display: flex;
  align-items: center;
  gap: 15px;
}

.lang-selector {
  background-color: transparent;
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 5px 10px;
  border-radius: 4px;
}

.btn-login {
  background-color: #4caf50;
  color: white;
  padding: 8px 15px;
  border-radius: 4px;
  text-decoration: none;
  transition: background-color 0.3s;
}

.btn-login:hover {
  background-color: #388e3c;
}

.user-menu {
  position: relative;
}

.user-info {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.user-dropdown {
  position: absolute;
  right: 0;
  top: 100%;
  background-color: white;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  width: 180px;
  z-index: 10;
  margin-top: 5px;
}

.dropdown-item {
  color: #333;
  padding: 10px 15px;
  text-decoration: none;
  display: block;
  transition: background-color 0.3s;
}

.dropdown-item:hover {
  background-color: #f5f5f5;
  cursor: pointer;
}
</style> 