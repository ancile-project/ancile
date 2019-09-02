<template lang="html">

  <div class="parentx">

    <vs-sidebar
      ref="sidebar"
      :reduce="true" 
      :reduce-not-rebound="true" 
      :reduce-not-hover-expand="false" 
      :hidden-background="true"
      color="primary" 
      class="sidebarx" 
      spacer v-model="active">

      <div class="header-sidebar" slot="header">
        <router-link to="/"><vs-icon color="white" size="30px" icon-pack="fas" icon="fa-fingerprint"></vs-icon></router-link>
      </div>


      <SidebarItem :inUser="true" :showAtLogout="true" :index="1" icon="fa-home" to="/" label="Home" />

      <SidebarItem :index="2" icon="fa-sign-in-alt" to="/login" label="Login" />
      <SidebarItem :index="3" icon="fa-user-plus" to="/signup" label="Signup" />

      <SidebarItem :inUser="true" :index="2" icon="fa-server" to="/providers" label="Providers" />
      <SidebarItem :inUser="true" :index="3" icon="fa-rocket" to="/apps" label="Apps" />

      <SidebarItem :inDeveloper="true" :index="1" icon="fa-terminal" to="/dev" label="Console" />
      <SidebarItem :index="4" :inUser="true" :inAdmin="true" :inDeveloper="true" :loggedIn="true" icon="fa-sign-out-alt" label="Logout" to="/logout" />

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
  }
}
</script>

<style>
.header-sidebar {
	display: flex;
	align-items: center;
	justify-content: center;
	flex-direction: column;
	width: 100%;
}

.vs-sidebar > header {
  background-color: rgb(var(--vs-primary));
}
</style>
