<template>
  <div id="content">
    <vs-row vs-justify="center">
      <vs-col type="flex" vs-justify="center" vs-align="center" vs-w="6">
        <vs-card class="cardx">
          <div slot="header">
            <h3>
              Settings
            </h3>
          </div>
          <span>Logged in as <strong>{{ $store.state.user.username }}</strong></span>
          <div class="centerx labelx">
            <Input
              v-for="(field, index) in fields"
              :key="index"
              v-model="fieldValues[field[0]]"
              :type="field[1]"
              :placeholder="field[2]"
              :error="errors[field[0]]"/>
          </div>
          <vs-button @click="sendForm()" :disabled='buttonOff || !allFilled' type="gradient">Update</vs-button>
        </vs-card>
        <vs-card class="cardx">
          <div slot="header">
            <h3>
              Become a developer
            </h3>
          </div>
          <div class="dev-status" v-if="$store.state.user.isDeveloper"> 
            You are a developer.
          </div>
          <div class="dev-status" v-else> 
            You are not a developer.
          </div>
          <vs-button @click="sendForm()" :disabled='$store.state.user.isDeveloper' type="gradient">Apply</vs-button>
        </vs-card>
      </vs-col>
    </vs-row>
  </div>
</template>

<script>
import Input from '@/components/Input.vue'

export default {
  name: "UserSettings",
  components: {
    Input
  },

  data() {
    return {
      fields: [["firstName", "text", "First name"],
              ["lastName", "text", "Last name"],
              ["email", "text", "Email address"],
              ["oldPassword", "password", "Old Password"],
              ["newPassword1", "password", "New Password"],
              ["newPassword2", "password", "Confirm password"]],
      errors: {},
      fieldValues: {
        oldPassword: "",
        newPassword1: "",
        newPassword2: "",
        firstName: this.$store.state.user.firstName,
        lastName: this.$store.state.user.lastName,
        email: this.$store.state.user.email,
      },
      buttonOff: false
    }
  },

  computed: {
    allFilled() {
      return this.fieldValues.firstName && this.fieldValues.lastName && this.fieldValues.email;
    }
  },

  methods: {
    sendForm() {
      const { firstName, email, lastName, oldPassword, newPassword1, newPassword2 } = this.fieldValues;

      this.errors = {};

      const payload = {
        firstName,
        lastName,
        email
      };

      if (newPassword1 || newPassword2) {
        let error = false;
        if (!oldPassword) {
          this.errors = {... this.errors, oldPassword: "Old password required for password change"};
          error = true;
        }

        if (newPassword1 !== newPassword2) {
          this.errors = {...this.errors, newPassword1: "Passwords do not match"};
          error = true;
        }

        if (error) return;

        payload.oldPassword = oldPassword;
        payload.newPassword = newPassword1;
      }

    }
  },
  mounted() {
    if (!this.$store.state.user.username) this.$store.dispatch("updateUserData")
    .then(() => {
      const {username, firstName, lastName, email} = this.$store.state.user;
      this.fieldValues = {
        ...this.fieldValues,
        firstName,
        lastName,
        email
      }
    })
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

.dev-status {
  margin-top: 0.5em;
  margin-bottom: 1em;
}
</style>