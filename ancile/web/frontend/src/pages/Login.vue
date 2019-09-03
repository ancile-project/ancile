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
    const { username, password } = this;
    this.$store.dispatch("login", { username, password })
      .then(() => {
        this.$root.notify("success", "Successfully logged in.");
        this.$router.push("/");
      })
      .catch((err) => {
        let msg = "Connection error."
        if (err.name === "AncileError") {
          msg = err.description;
        }

        this.$root.notify("fail", msg);
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