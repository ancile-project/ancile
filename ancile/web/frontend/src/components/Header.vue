<template>
  <div id="header">
    <vs-row vs-justify="space-between">
      <vs-col vs-offset="4" type="flex" vs-justify="center" vs-align="center" vs-w="4">
          <div id="title">
            <router-link to="/">
              <h2 id="title-text">
                Ancile
              </h2>
            </router-link>
          </div>
      </vs-col>
      <vs-col style="text-align:center" type="flex" vs-justify="center" vs-align="center" vs-w="1">
        <vs-dropdown v-if="state.user.isDeveloper || state.user.isSuperuser" id="user-dropdown" vs-custom-content vs-trigger-click>
          <vs-button class="btn-drop" type="filled" icon-pack="fas" icon="fa-user"/>
          <!-- <a href="#">Hola mundo</a> -->

          <vs-dropdown-menu class="loginx">
            <div id="user-dropdown-content">
              <h3 v-bind="redirect">
                Mode:
              </h3>
                <vs-radio v-model="activeMode" vs-name="User" vs-value="user">User</vs-radio>
                <vs-radio v-if="state.user.isDeveloper" v-model="activeMode" vs-name="Developer" vs-value="dev">Developer</vs-radio>
                <vs-radio v-if="state.user.isSuperuser" v-model="activeMode" vs-name="Admin" vs-value="admin">Admin</vs-radio>
            </div>
          </vs-dropdown-menu>
        </vs-dropdown>
      </vs-col>
    </vs-row>
  </div>
</template>


<script>
export default {
  name: "Header",
  
  data() {
    return { 
      activeMode: "user",
      state: this.$root,
    }
  },
  computed: {
    redirect() {
      this.activeMode === "user" ? "" : this.$router.push("/" + this.activeMode);
    }
  }
}
</script>

<style>
#header {
  display: flex;
  align-items: center;
  background-color: rgb(var(--vs-primary), 1);
  height: 52px;
  width: 100%;
}

#title-text {
  color: white;
  text-align: center;
}

#user-dropdown > .btn-drop {
  height: 25px !important;
}

#user-dropdown-content {
  padding: 5px 10px;
}

#user-dropdown-content > .vs-radio-primary {
  justify-content: left;
}
</style>