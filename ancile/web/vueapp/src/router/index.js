import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/pages/Home'
import Login from '@/pages/Login'
import Signup from '@/pages/Signup'

import UserProviders from '@/pages/user/UserProviders'

Vue.use(Router)

const loggedOutOnlyPaths = ["/login", "/signup"]
const anyState = ["/"]

export default function(state, logout) {
  const router = new Router({
    routes: [
      {
        path: '/',
        name: 'Home',
        component: Home
      },
      {
        path: '/login',
        name: 'Login',
        component: Login
      },
      {
        path: '/signup',
        name: 'Signup',
        component: Signup
      },
      {
        path: '/providers',
        name: 'UserProviders',
        component: UserProviders
      }
    ]
  })

  router.beforeEach(function(to, from, next) {
    if (to.path === "/logout") {
      logout();
      return next('/');
    }

    if (state.loggedIn) {
      if (loggedOutOnlyPaths.includes(to.path)) return next('/');
    } else if (!(loggedOutOnlyPaths.includes(to.path) || anyState.includes(to.path))) {
      return next('/login')
    }

    return next();

  })
  return router;
}