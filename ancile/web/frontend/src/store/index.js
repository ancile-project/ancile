import Vue from 'vue';
import VueCookie from 'vue-cookies';
import Vuex from 'vuex';
import axios from 'axios';

Vue.use(VueCookie)
Vue.use(Vuex); 

const defaultUser = {
  id: -1,
  firstName: "",
  lastName: "",
  isDeveloper: false,
  isSuperuser: false
}

export default new Vuex.Store({
  state: {
    loggedIn: Vue.cookies.get("csrftoken") && document.getElementById("loggedin") ? true: false,
    mode: "user",
    user: {...defaultUser}
  },

  mutations: {
    updateLoggedIn(state, loggedIn) {
      state.loggedIn = loggedIn;
    },

    updateUser(state, user) {
      state.user = user;
    },

    setMode(state, mode) {
      if (state.mode === mode) return;
      state.mode = mode;
    }
  },

  actions: {
    async login(context, { username, password }) {
      const response = await context.dispatch("post", {endpoint: "/login/", data: {username, password}});

      if (response.data.status === 'ok') {
        context.commit("updateLoggedIn", true);
        context.dispatch("updateUserData");
        return response;
      }
      
      throw new {
        name: "AncileError",
        description: response.data.error
      };

    },

    async logout(context) {
      return await axios.get('/logout/')
        .then(() => {
          context.commit("updateLoggedIn", false);
          context.commit("updateUser", {...defaultUser});
        });
    },

    async post({}, { endpoint, data }) {
      axios.defaults.headers["X-CSRFToken"] = Vue.cookies.get("csrftoken");
      return await axios.post(endpoint, data);
    },

    async updateUserData(context) {
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

      context.dispatch("query", query)
      .then(resp => context.commit('updateUser', resp.currentUser));
    },

    async query(context, query) {
      const response = await context.dispatch("post", {
        endpoint: '/api/graphene', 
        data: {query: query}
      });

      return response.data.data;
    },
  }
});