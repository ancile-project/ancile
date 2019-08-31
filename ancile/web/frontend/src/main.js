import Vue from 'vue'
import App from './App.vue'
import Vuesax from 'vuesax'
import routerFactory from './router'
import 'vuesax/dist/vuesax.css'
import VueCookie from 'vue-cookies'
import axios from 'axios';

Vue.config.productionTip = false

Vue.use(Vuesax)
Vue.use(VueCookie)

const state = {
  loggedIn: false,
};

if (Vue.cookies.get("csrftoken") && document.getElementById("loggedin")) {
  state.loggedIn = true;
}
// This is the logout function, it takes care of
// changing the state.
function logout() {
  axios.get('/logout')
  .then(() => {
    state.loggedIn = false;
    Vue.prototype.$vs.notify({
      title: "Sucessfully logged out.",
      icon: "fa-check",
      iconPack: "fas",
      color: "success",
      position: "top-center"
    })
  })
  .catch(() => {
    Vue.prototype.$vs.notify({
      title: "Error while logging out.",
      icon: "fa-check",
      iconPack: "fas",
      color: "danger",
      position: "top-center"
    })
  })
}

const router = routerFactory(state, logout);

new Vue({
  data: state,
  methods: {
  login(username, password) {
    this.postRequest("/login", {username, password})
      .then(response => {
        if (response.data.status === 'ok') {
          this.notify("success", "Sucessfully logged in!");
          this.loggedIn = true;
          this.$router.push("/");
        } else if (response.data.status === 'error') {
          this.notify("fail", response.data.error)
        }
      })
      .catch(() => {
        this.notify("fail", "Connection error.");
      })

    },
    logout,
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

    postRequest(endpoint, data) {
      axios.defaults.headers["X-CSRFToken"] = Vue.cookies.get("csrftoken");
      return axios.post(endpoint, data);
    },

    async dataFetch(query, callback) {
      this.$vs.loading();

      await this.postRequest('/api/graphene', {query: query})
      .then(resp => {
        if (resp.status === 200) callback(resp.data.data)
      })
      .catch(err => {
        if (err.response.status === 403) {
          this.notify("fail", "Your session has expired.");
          this.loggedIn = false;
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
  render: h => h(App),
  router,
}).$mount('#app')
