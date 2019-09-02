<template>
  <div id="content">
    <vs-row vs-justify="center">
      <vs-col type="flex" vs-justify="center" vs-align="center" vs-w="6">
        <vs-card class="cardx">
          <div slot="header">
            <h3>
              Welcome to Ancile!
            </h3>
          </div>
          <div slot="media">
            <img src="../assets/ancile.png"/>
          </div>
          <div>
            <span>
              Ancile is a light, flexible framework for privacy-aware applications.
            </span>
            <div v-if="loggedIn" class="login-buttons">
              <vs-button type="gradient" color="danger" to="/logout">Logout</vs-button>
            </div>
            <div v-else class="login-buttons">
              <vs-button type="gradient" to="/login">Login</vs-button>
              <vs-button type="gradient" to="/signup">Signup</vs-button>
            </div>
          </div>
        </vs-card>
      </vs-col>
    </vs-row>
  </div>
</template>

<script>
import { mapState } from 'vuex';

export default {
  name: 'Home',
  computed: mapState({
    loggedIn: "loggedIn"
  })
}
</script>

<style>
#content {
  text-align: center;
}

body {
  background-color: #ffffff;
}

.login-buttons > button {
  margin: 10px 5px;
}
</style>