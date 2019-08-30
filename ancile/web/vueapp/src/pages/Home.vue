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
            <div class="login-buttons">
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
export default {
  name: 'Home'
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