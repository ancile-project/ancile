import Vue from 'vue';
import Vuesax from 'vuesax';
import 'vuesax/dist/vuesax.css';

import App from './App.vue';
import router from './router';
import store from './store';

Vue.use(Vuesax);

new Vue({
  methods: {

    notify(type, title, text) {
      var icon = "fa-info";
      var color = "primary";

      if (type === "success") {
        icon = "fa-check";
        color = "success";
      } else if (type === "fail") {
        icon = "fa-times";
        color = "danger";
      }

      this.$vs.notify({
        title: title,
        text: text,
        color: color,
        position: "top-center",
        icon: icon,
        iconPack: "fas"
      })
    },

    async query(query) {
      this.$vs.loading();

      let output = {};

      await this.$store.dispatch("query", query)
      .then(r => output = r)
      .catch(err => {
        if (err.response.status === 403) {
          this.notify("fail", "Your session has expired.");
          this.$router.push('/login');
        } else if (err.response.status === 500) {
          this.notify("fail", "Server side error.");
        } else if (err.response.status === 400) {
          this.notify("fail", "Query error.")
        }
      })
      .catch(() => {
        this.notify("fail", "Connection error.");
      })
      .then(() => this.$vs.loading.close())

      return output;

    },

    listToObject(list) {
      let obj = {};

      list.forEach(el => {
        obj[el.id] = el;
      })

      return obj;
    },
  },
  created() {
    if (store.state.loggedIn) store.dispatch("updateUserData");
  },
  store,
  render: h => h(App),
  router,
}).$mount('#app');
