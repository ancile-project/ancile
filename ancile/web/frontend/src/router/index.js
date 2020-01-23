import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/pages/Home'
import Login from '@/pages/Login'
import Signup from '@/pages/Signup'

import UserApps from '@/pages/user/UserApps'
import UserProviders from '@/pages/user/UserProviders'
import UserSettings from '@/pages/user/UserSettings'

import SubView from '@/components/SubView'

import DevApps from '@/pages/dev/DevApps'
import DevAppsTable from '@/pages/dev/DevAppTable'
import DevAppView from '@/pages/dev/DevAppView'
import DevConsole from '@/pages/dev/DevConsole'

import AdminApps from '@/pages/admin/AdminApps'
import AdminAppsTable from '@/pages/admin/AdminAppTable'
import AdminAppView from '@/pages/admin/AdminAppView'
import AdminConsole from '@/pages/admin/AdminConsole'
import AdminProviders from '@/pages/admin/AdminProviders'

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
      component: SubView,
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
          ]
        }
      ]
    },
    {
      path: '/admin',
      component: SubView,
      children: [
        {
          path: "",
          name: 'AdminConsole',
          component: AdminConsole
        },
        {
          path: "apps",
          component: AdminApps,
          children: [
            {
              path: "",
              name: 'AdminAppsTable',
              component: AdminAppsTable
            },
            {
              path: ":id",
              name: 'AdminAppView',
              component: AdminAppView,
            },
          ]
        },
        {
          path: "providers",
          name: "AdminProviders",
          component: AdminProviders,
        }
      ]
    } 

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
