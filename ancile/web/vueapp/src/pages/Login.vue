<template>
  <div id="content">
    <vs-row vs-justify="center">
      <vs-col type="flex" vs-justify="center" vs-align="center" vs-w="6">
        <vs-card class="cardx">
          <div slot="header">
            <h3>
              Login
            </h3>
          </div>
          <span>Don't have an account? <router-link to="/signup">Sign up</router-link></span>
          <div class="centerx labelx">
            <vs-input placeholder="Username" v-model="username"/>
            <vs-input type="password" placeholder="Password" v-model="password"/>
          </div>
          <vs-button @click="login()" type="gradient">Login</vs-button>
        </vs-card>
      </vs-col>
    </vs-row>
  </div>
</template>

<script>
export default {
  name: "Login",

  data() {
    return {
      username: "",
      password: ""
    }
  },
  methods: {
  login() {
    const data = new FormData();
    data.set('username', this.username);
    data.set('password', this.password);
    this.$root.postRequest("/login/", data)
      .then(response => {
        if (response.status === 200) {
          this.$root.notify("success", "Sucessfully logged in!");
          this.$root.loggedIn = true;
          this.$router.push("/");
        }
      })
      .catch(error => {
        if (error.response.status === 400) {
          this.$root.notify("fail", "Incorrect username or password.");
        }
      })
      .catch(() => {
        this.$root.notify("fail", "Connection error.");
      })

    }
  },
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