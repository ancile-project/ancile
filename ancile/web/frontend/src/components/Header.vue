<template>
  <div id="header">
    <vs-row vs-align="center" vs-justify="space-between" vs-w="12">
      <vs-col type="flex" vs-justify="center" vs-align="center" vs-w="4">
        <vs-icon id="header-icon" size="30px" color="white" icon-pack="fas" icon="fa-fingerprint" />
      </vs-col>
      <vs-col type="flex" vs-justify="center" vs-align="center" vs-w="4">
          <div id="title">
            <router-link to="/">
              <h2 id="title-text">
                Ancile
              </h2>
            </router-link>
          </div>
      </vs-col>
      <vs-col style="text-align:right" type="flex" vs-justify="center" vs-align="center" vs-w="4">
        <vs-dropdown v-if="user.isSuperuser || user.isDeveloper" id="user-dropdown" vs-custom-content vs-trigger-click>
          <vs-button class="btn-drop" type="filled" icon-pack="fas" icon="fa-user"/>
          <!-- <a href="#">Hola mundo</a> -->

          <vs-dropdown-menu class="loginx">
            <div id="user-dropdown-content">
              <h3>
                Mode:
              </h3>
                <vs-radio v-model="mode" vs-name="User" vs-value="user">User</vs-radio>
                <vs-radio v-if="user.isDeveloper" v-model="mode" vs-name="Developer" vs-value="dev">Developer</vs-radio>
                <vs-radio v-if="user.isSuperuser" v-model="mode" vs-name="Admin" vs-value="admin">Admin</vs-radio>
            </div>
          </vs-dropdown-menu>
        </vs-dropdown>
      </vs-col>
    </vs-row>
  </div>
</template>


<script>
import { mapState } from 'vuex';
export default {
  name: "Header",
  
  computed: {

    ...mapState(["user"]),

    mode: {
      get() {
        return this.$store.state.mode;
      },

      set(mode) {
        this.$store.commit("setMode", mode);
      }
    }

  }, 

  watch: {
    mode(m) {
      const path = "/" + (m === "user" ? "" : m);
      this.$router.push(path);
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


#user-dropdown-content {
  padding: 5px 10px;
}

#user-dropdown-content > .vs-radio-primary {
  justify-content: left;
}

#header-icon {
  margin-left: 12px;
}
</style>