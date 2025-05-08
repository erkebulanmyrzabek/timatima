import { createStore } from 'vuex';
import auth from './modules/auth';
import news from './modules/news';
import lawyers from './modules/lawyers';
import mail from './modules/mail';
import pgp from './modules/pgp';

export default createStore({
  modules: {
    auth,
    news,
    lawyers,
    mail,
    pgp
  }
}); 