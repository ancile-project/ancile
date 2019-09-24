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
            <Input
              v-for="(field, index) in fields"
              :key="index"
              v-model="fieldValues[field[0]]"
              :type="field[1]"
              :placeholder="field[2]"
              :error="errors[field[0]]"/>
          </div>
          <vs-button @click="sendForm()" :disabled='buttonOff || !allFilled' type="gradient">Sign up</vs-button>
        </vs-card>
      </vs-col>
    </vs-row>
  </div>
</template>

<script>
import Input from '@/components/Input.vue'

export default {
  name: "Signup",
  components: {
    Input
  },

  data() {
    return {
      fields: [["username", "text", "Username"],
              ["password1", "password", "Password"],
              ["password2", "password", "Confirm password"],
              ["firstName", "text", "First name"],
              ["lastName", "text", "Last name"],
              ["email", "text", "Email address"]],
      errors: {},
      fieldValues: {
        username: "",
        password1: "",
        password2: "",
        firstName: "",
        lastName: "",
        email: "",
      },
      buttonOff: false
    }
  },

  computed: {
    allFilled() {
      return this.fields
        .map(field => this.fieldValues[field[0]])
        .reduce((prev, curr) => prev && curr, true)
    }
  },

  methods: {
    sendForm() {
      const { username, firstName, email, lastName, password1, password2 } = this.fieldValues;

      this.errors = {};

      if (password1 !== password2) {
        this.errors = {...this.errors, password2: "Your passwords do not match."};
        return;
      }

      const password = password1;

      const payload = {
        username,
        password,
        firstName,
        lastName,
        email
      }

      this.$store.dispatch("post", {endpoint: "/signup/", data: payload})
        .then(resp => {
          if (resp.data.ok) {
            this.$root.notify("success", "Sucessfully signed up");
            this.$store.dispatch("login", {username, password})
              .then(() => this.$router.push("/"));
          } else {
            this.$root.notify("fail", "Sign up failed");
            this.errors = {...this.errors, ...resp.data.errors};
          }
        })
        .catch(() => {
          this.$root.notify("fail", "Connection error");
        })
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