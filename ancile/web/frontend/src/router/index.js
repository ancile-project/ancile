import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/pages/Home'
import Login from '@/pages/Login'
import Signup from '@/pages/Signup'

import UserApps from '@/pages/user/UserApps'
import UserProviders from '@/pages/user/UserProviders'
import UserSettings from '@/pages/user/UserSettings'

import Dev from '@/pages/dev/Dev'
import DevApps from '@/pages/dev/DevApps'
import DevAppsTable from '@/pages/dev/DevAppsTable'
import DevAppView from '@/pages/dev/DevAppView'
import DevConsole from '@/pages/dev/DevConsole'
import DevGroupView from '@/pages/dev/DevGroupView'


import store from '@/store';

Vue.use(Router);

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
    },
    {
      path: '/signup',
      name: 'Signup',
      component: Signup,
    },
    {
      path: '/apps',
      name: 'UserApps',
      component: UserApps,
    },
    {
      path: '/providers',
      name: 'UserProviders',
      component: UserProviders,
    },
    {
      path: '/settings',
      name: 'Settings',
      component: UserSettings,
    },
    {
      path: '/dev',
      component: Dev,
      children: [
        {
          path: "",
          name: 'DevConsole',
          component: DevConsole
        },
        {
          path: "apps",
          component: DevApps,
          children: [
            {
              path: "",
              name: 'DevAppsTable',
              component: DevAppsTable
            },
            {
              path: ":id",
              name: 'DevAppView',
              component: DevAppView,
            },
            {
              path: ":id/group/:groupid",
              name: 'DevGroupView',
              component: DevGroupView
            }
          ]
        }
      ]
    },

  ]});

const logoutRequired = {
  '/login': true,
  '/register': true
};

const loginRequired = {
  '/apps': true,
  '/providers': true,
  '/settings': true,
  '/logout': true,
  '/dev': true
};

router.beforeEach(async function(to, from, next) {
  const { path } = to;

  let loggedIn = store.state.loggedIn;

  if (path === '/logout') {
    store.dispatch("logout");
    return from.path === "/" ? "" : next('/');
  }

  if (!loggedIn && loginRequired[path]) {
    return next('/login')
  } else if (loggedIn && logoutRequired[path]) {
    return next('/')
  } else {
    next()
  }

  if (to.path.startsWith("/dev")) {
    store.state.mode = "dev";
  } else if (to.path.startsWith("/admin")) {
    store.state.mode = "admin";
  } else {
    store.state.mode = "user"
  }

});

export default router;
