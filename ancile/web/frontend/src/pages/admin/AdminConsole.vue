<template>
  <Table 
  header="Pending Developers"
  :fields="fields"
  :actions="actions"
  :data="data"/>
</template>

<script>
import Table from '@/components/Table';

export default {
  name: "DevConsole",
  components: {
    Table
  },
  data() {
    return {
      fields: [
        {
          title: "Name",
          value: "fullName"
        },
        {
          title: "Username",
          value: "username"
        }
      ],
      actions: [
        {
          color: "success",
          icon: "fa-check",
          callback: u => this.mutateDev(u.id, true)
        },
        {
          color: "danger",
          icon: "fa-times",
          callback: u => this.mutateDev(u.id, false)
        }
      ],
      data: [],
    }
  },
  methods: {

    async getData() {
      const query = `{
        pendingDevelopers {
          id
          username
          firstName
          lastName
        }
      }`;

      await this.$root.getData(query)
        .then(resp => {
          this.data = resp.pendingDevelopers.map(u => ({...u, fullName: u.firstName + " " + u.lastName}));
        });
    },

    async mutateDev(id, approve) {
      const query = `
      mutation mutateDev($id: Int, $approve: Boolean) {
        updateUser(user: $id, isDeveloper: $approve) {
          ok
          error
        }
      }
      `

      const args = {
        id,
        approve
      }

      const msg = approve ? "approved" : "declined";

      this.$root.getData(query, args)
        .then(resp => {
          if (resp.updateUser.ok) {
            this.$root.notify("success", "Developer application " + msg);
          } else {
            this.$root.notify("error", this.resp.updateUser.error);
          }
        })
        .catch(() => {
            this.$root.notify("fail", "An error has occurred.");
          }
        )
        .then(this.getData);
    },
  },
  created() {
    this.getData();
  }
}
</script>

<style>

</style>