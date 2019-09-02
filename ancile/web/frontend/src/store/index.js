import Vue from 'vue';
import VueCookie from 'vue-cookies';
import Vuex from 'vuex';

Vue.use(VueCookie)
Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    loggedIn: Vue.cookies.get("csrftoken") && document.getElementById("loggedin") ? true: false,
    mode: "user",
    user: {
      id: -1,
      firstName: "",
      lastName: "",
      isDeveloper: false,
      isSuperuser: false
    }
  },

  mutations: {
    updateUser(state, user) {
      state.user = {...state.user, ...user};
    },

    setMode(state, mode) {
      if (state.mode === mode) return;
      state.mode = mode;
    }
  }
});