import Vue from 'vue';
import Vuesax from 'vuesax';
import 'vuesax/dist/vuesax.css';

import App from './App.vue';
import router from './router';
import store from './store';

Vue.use(Vuesax);

new Vue({

  methods: {

    async oauth(provider) {
      const url = "/oauth/" + provider.pathName;
      const w = window.open(url);

      return new Promise((resolve) => {
        const refreshId = setInterval(() => {
          if (w.closed) {
            resolve();
            clearInterval(refreshId);
          }
        }, 1000);
      });
    },

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

    async getData(query, args) {
      this.$vs.loading();

      let output = {};

      if (args === undefined) args = {};

      await this.$store.dispatch("query", { query, args })
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

  },
  created() {
    if (store.state.loggedIn) store.dispatch("updateUserData");
  },
  store,
  render: h => h(App),
  router,
}).$mount('#app');
