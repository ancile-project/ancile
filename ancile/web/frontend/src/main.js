import axios from 'axios';
import Vue from 'vue';
import Vuesax from 'vuesax';
import 'vuesax/dist/vuesax.css';

import App from './App.vue';
import router from './router';
import store from './store';

Vue.use(Vuesax);

new Vue({
  data() {
    return {
      loggedIn: this.$cookies.get("csrftoken") && document.getElementById("loggedin") ? true: false,
      activeMode: "user",
      user: {}
    }
  },
  methods: {
  getUserData() {
    const query = `
    {
      currentUser {
        username
        firstName
        lastName
        email
        isSuperuser
        isDeveloper
      }
    }
    `
  
    this.query(query, (resp) => {
      store.commit('updateUser', resp.currentUser);
    })
  },

  login(username, password) {
    this.post("/login/", {username, password})
      .then(response => {
        if (response.data.status === 'ok') {
          this.notify("success", "Sucessfully logged in!");
          this.getUserData();
          store.loggedIn = true;
          this.$router.push("/");
        } else if (response.data.status === 'error') {
          this.notify("fail", response.data.error)
        }
      })
      .catch(() => {
        this.notify("fail", "Connection error.");
      })

    },

    logout() {
      axios.get('/logout/')
      .then(() => {
        store.loggedIn = false;
        store.user = {};
        this.notify("success", "Sucessfully logged out.")
      })
      .catch(() => this.notify("fail", "Error while logging out."))
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

    async post(endpoint, data) {
      axios.defaults.headers["X-CSRFToken"] = Vue.cookies.get("csrftoken");
      return await axios.post(endpoint, data);
    },

    async query(query, callback) {
      this.$vs.loading();

      await this.post('/api/graphene', {query: query})
        .then(resp => {
          if (resp.status === 200) callback(resp.data.data)
        })
        .catch(err => {
          if (err.response.status === 403) {
            this.notify("fail", "Your session has expired.");
            store.loggedIn = false;
            store.commit('updateUser', resp.currentUser);
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

      this.$vs.loading.close();

    },

    listToObject(list) {
      let obj = {};

      list.forEach(el => {
        obj[el.id] = el;
      })

      return obj;
    }
  },
  watch: {
    activeMode(mode) {
      if (mode === "user") {
        this.$router.push("/");
      }
      else { 
        this.$router.push("/" + mode);
      }
    }
  },
  created() {
    if (store.state.loggedIn) this.getUserData();
  },
  store,
  render: h => h(App),
  router,
}).$mount('#app');
