<template>
  <footer class="footer">
    <div class="container footer-content">
      <div class="footer-logo">
        <div class="logo-wrapper">
          <img src="@/assets/images/logo-white.svg" alt="Дом Адвокатов" />
          <span>DOM ADVOKATOV</span>
        </div>
        <p class="footer-description">
          Профессиональная юридическая помощь и консультации от опытных адвокатов. Мы помогаем решать сложные правовые вопросы и обеспечиваем защиту ваших интересов.
        </p>
      </div>
      
      <div class="footer-links">
        <h4>Главная</h4>
        <ul>
          <li><router-link to="/about">О компании</router-link></li>
          <li><router-link to="/association">Задачи Ассоциации</router-link></li>
          <li><router-link to="/news">Последние новости</router-link></li>
          <li><router-link to="/achievements">Наши достижения</router-link></li>
          <li><router-link to="/contacts">Контакты</router-link></li>
        </ul>
      </div>
      
      <div class="footer-links">
        <h4>Новости</h4>
        <ul>
          <li><router-link to="/news">Главная</router-link></li>
          <li><router-link to="/news/category/law">Законодательство</router-link></li>
          <li><router-link to="/news/category/events">События</router-link></li>
          <li><router-link to="/news/category/court">Судебная практика</router-link></li>
        </ul>
      </div>
      
      <div class="footer-links">
        <h4>Форумы</h4>
        <ul>
          <li><router-link to="/forums">Главная</router-link></li>
          <li><router-link to="/forums/civil">Гражданское право</router-link></li>
          <li><router-link to="/forums/criminal">Уголовное право</router-link></li>
          <li><router-link to="/forums/admin">Административное право</router-link></li>
        </ul>
      </div>
    </div>
    
    <div class="footer-bottom">
      <div class="container">
        <div class="social-links">
          <a href="https://linkedin.com" target="_blank"><i class="fab fa-linkedin"></i></a>
          <a href="https://instagram.com" target="_blank"><i class="fab fa-instagram"></i></a>
        </div>
        <div class="copyright">
          © Dom advokatov 2025. Все права защищены.
        </div>
        <div class="privacy-policy">
          <router-link to="/privacy">Политика конфиденциальности</router-link>
        </div>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'AppFooter'
}
</script>

<style scoped>
.footer {
  background-color: #1a3a34;
  color: white;
  padding-top: 40px;
  margin-top: auto;
}

.footer-content {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 40px;
  padding-bottom: 40px;
}

.logo-wrapper {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.logo-wrapper img {
  height: 30px;
  margin-right: 10px;
}

.footer-description {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  line-height: 1.6;
}

.footer-links h4 {
  margin-bottom: 15px;
  font-size: 1.1rem;
  font-weight: 500;
}

.footer-links ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links li {
  margin-bottom: 10px;
}

.footer-links a {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: color 0.3s;
}

.footer-links a:hover {
  color: #4caf50;
}

.footer-bottom {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px 0;
}

.footer-bottom .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.social-links {
  display: flex;
  gap: 15px;
}

.social-links a {
  color: white;
  font-size: 1.2rem;
}

.copyright {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.9rem;
}

.privacy-policy a {
  color: rgba(255, 255, 255, 0.5);
  text-decoration: none;
  font-size: 0.9rem;
}

.privacy-policy a:hover {
  text-decoration: underline;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .footer-content {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 480px) {
  .footer-content {
    grid-template-columns: 1fr;
  }
  
  .footer-bottom .container {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
}
</style> 