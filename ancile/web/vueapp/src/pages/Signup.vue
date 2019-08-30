<template>
  <div id="content">
    <vs-row vs-justify="center">
      <vs-col type="flex" vs-justify="center" vs-align="center" vs-w="6">
        <vs-card class="cardx">
          <div slot="header">
            <h3>
              Sign up
            </h3>
          </div>
          <span>Already have an account? <router-link to="/login">Login</router-link></span>
          <div class="centerx labelx">
            <vs-input placeholder="Username" v-model="username"/>
            <vs-input type="password" placeholder="Password" v-model="password1"/>
            <vs-input type="password" placeholder="Confirm password" v-model="password2"/>
            <vs-input placeholder="First Name" v-model="firstName"/>
            <vs-input placeholder="Last Name" v-model="lastName"/>
            <vs-input placeholder="Email" v-model="email"/>
          </div>
          <vs-button type="gradient">Sign up</vs-button>
        </vs-card>
      </vs-col>
    </vs-row>
  </div>
</template>

<script>
export default {
  name: "Signup",

  data() {
    return {
      username: "",
      password1: "",
      password2: "",
      firstName: "",
      lastName: "",
      email: ""
    }
  }
}
</script>


<style lang="scss" scoped>

.labelx {
  margin-bottom: 15px;

  .vs-input {
    margin: 15px auto;
  }
}
</style>