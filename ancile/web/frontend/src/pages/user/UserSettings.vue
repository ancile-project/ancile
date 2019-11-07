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
          <div class="dev-status" v-else-if="$store.state.user.isPendingDeveloper"> 
            Your developer application is pending.
          </div>
          <div class="dev-status" v-else> 
            You are not a developer.
          </div>
          <vs-button @click="becomeDeveloper()" :disabled='$store.state.user.isDeveloper || $store.state.user.isPendingDeveloper' type="gradient">Apply</vs-button>
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
    },
  },

  methods: {
    query(query, variables) {
      const args = {...variables, user: this.$store.state.user.id}
      this.$store.dispatch("query", { query, args })
        .then(resp => {
          if (resp.updateUser.ok) {
            this.$root.notify("success", "Profile updated successfully");
          } else {
            this.$root.notify("fail", resp.updateUser.error);
          }
        })
        .catch(() => {
          this.$root.notify("fail", "Connection error");
        })
        .then(() => {
          this.updateUserData();
          this.buttonOff = false;
        });
    },
    becomeDeveloper() {
      const query = `
      mutation becomeDeveloper($user: Int) {
        updateUser(user: $user, pendingDeveloper: true) {
          ok
          error
        }
      }`
      this.query(query, {});
    },



    sendForm() {
      const { firstName, email, lastName, oldPassword, newPassword1, newPassword2 } = this.fieldValues;
      this.errors = {};
      this.buttonOff = true;

      const query = `mutation updateUser($user: Int, $firstName: String, $lastName: String, $email: String, $oldPassword: String, $newPassword: String) {
        updateUser(user: $user, firstName: $firstName, lastName: $lastName, email: $email, oldPassword: $oldPassword, newPassword: $newPassword) {
          ok
          error
        }
      }`

      const args = {
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

        args.oldPassword = oldPassword;
        args.newPassword = newPassword1;
        
      }

      this.query(query, args);

    },
    updateUserData() {
      this.$store.dispatch("updateUserData")
        .then(() => {
          const {firstName, lastName, email} = this.$store.state.user;
          this.fieldValues = {
            ...this.fieldValues,
            firstName,
            lastName,
            email
          }
      })
    }
  },
  mounted() {
    if (!this.$store.state.user.username) this.updateUserData();
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