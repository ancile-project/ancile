<template lang="html">

  <div id="sidebar">

    <vs-sidebar
      ref="sidebar"
      :click-not-close="true"
      :reduce="true" 
      :reduce-not-rebound="true" 
      :reduce-not-hover-expand="false" 
      :hidden-background="true"
      color="primary" 
      class="sidebarx" 
      spacer v-model="active">


      <SidebarItem :inUser="true" :showAtLogout="true" :index="1" icon="fa-home" to="/" label="Home" />

      <SidebarItem :index="2" icon="fa-sign-in-alt" to="/login" label="Login" />
      <SidebarItem :index="3" icon="fa-user-plus" to="/signup" label="Signup" />

      <SidebarItem :inUser="true" :index="2" icon="fa-server" to="/providers" label="Providers" />
      <SidebarItem :inUser="true" :index="3" icon="fa-rocket" to="/apps" label="Apps" />
      <SidebarItem :inUser="true" :index="4" icon="fa-cog" to="/settings" label="Settings" />

      <SidebarItem :inDeveloper="true" :index="1" icon="fa-terminal" to="/dev" label="Console" />
      <SidebarItem :inDeveloper="true" :index="2" icon="fa-rocket" to="/dev/apps" label="Apps" />

      <SidebarItem :inAdmin="true" :index="1" icon="fa-terminal" to="/admin" label="Console" />
      <SidebarItem :inAdmin="true" :index="2" icon="fa-rocket" to="/admin/apps" label="Applications" />
      <SidebarItem :inAdmin="true" :index="3" icon="fa-server" to="/admin/providers" label="Providers" />


      <SidebarItem :index="5" :inUser="true" :inAdmin="true" :inDeveloper="true" :loggedIn="true" icon="fa-sign-out-alt" label="Logout" to="/logout" />

    </vs-sidebar>

  </div>

</template>

<script>
import SidebarItem from './SidebarItem.vue';

export default {
  data:()=>({
    active:true,
  }),
  components: {
    SidebarItem
  },
  methods: {
    refreshActive() {
      this.$refs.sidebar.$children.forEach(child => {
        if (typeof child.checkActive === "function") {
          child.checkActive();
        }
      })
    },
  },
  mounted() {
  const el = document.getElementsByClassName("vs-sidebar")[0];

  window.onscroll = () => {

    if (window.scrollY > 52) {
        el.classList.add("scrolled");
    } else {
      el.classList.remove("scrolled");
    }
  }
  }
}
</script>

<style>
.vs-sidebar-parent.vs-sidebar {
  top: 52px;
  height: calc(100% - 52px) !important;
  z-index: 99;
}

.vs-sidebar-parent.vs-sidebar.scrolled {
  top: 0px;
  height: 100% !important;
  position: fixed; 
}
</style>
