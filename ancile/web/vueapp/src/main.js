import Vue from 'vue'
import App from './App.vue'
import Vuesax from 'vuesax'
import routerFactory from './router'
import 'vuesax/dist/vuesax.css'
import VueCookie from 'vue-cookies'
import axios from 'axios';
import 'material-icons/iconfont/material-icons.css';

Vue.config.productionTip = false

Vue.use(Vuesax)
Vue.use(VueCookie)

const state = {
  loggedIn: false,
};

let token = Vue.cookies.get("csrftoken");
axios.defaults.headers["X-CSRFToken"] = token;

if (token && document.getElementById("loggedin")) {
  state.loggedIn = true;
}
// This is the logout function, it takes care of
// clearing the cookies and changing the state.
const router = routerFactory(state, () => {
  state.loggedIn = false;
  Vue.prototype.$vs.notify({
    title: "Sucessfully logged out.",
    icon: "fa-check",
    iconPack: "fas",
    color: "success",
    position: "top-center"
  })
});

new Vue({
  data: state,
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
    postRequest(endpoint, data) {
      if (!token) {
        token = Vue.cookies.get("csrftoken");
        axios.defaults.headers["X-CSRFToken"] = token;
      }
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