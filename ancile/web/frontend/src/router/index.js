import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/pages/Home'
import Login from '@/pages/Login'
import Signup from '@/pages/Signup'

import UserApps from '@/pages/user/UserApps'
import UserProviders from '@/pages/user/UserProviders'

Vue.use(Router)

export default function(state, logout) {
  const loggedOutOnly = (to, from, next) => state.loggedIn ? next('/') : next();
  const loggedInOnly = (to, from, next) => !state.loggedIn ? next('/') : next();

  const router = new Router({
    routes: [
      {
        path: '/',
        name: 'Home',
        component: Home,
      },
      {
        path: '/login',
        name: 'Login',
        component: Login,
        beforeEnter: loggedOutOnly
      },
      {
        path: '/logout',
        beforeEnter(to, from, next) {
          logout();
          from.path === "/" ? "" : next('/');
        }
      },
      {
        path: '/signup',
        name: 'Signup',
        component: Signup,
        beforeEnter: loggedOutOnly
      },
      {
        path: '/apps',
        name: 'UserApps',
        component: UserApps,
        beforeEnter: loggedInOnly
      },
      {
        path: '/providers',
        name: 'UserProviders',
        component: UserProviders,
        beforeEnter: loggedInOnly
      }
    ]
  })

  return router;
}