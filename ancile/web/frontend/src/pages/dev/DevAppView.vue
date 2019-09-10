<template>
  <div>
      <div>
        <h3>
          <router-link to="/dev/apps/"><vs-icon color="primary" icon-pack="fas" icon="fa-arrow-left"/></router-link>
          {{ name }}
        </h3>
      </div>

    <vs-card>
      <vs-list>
        <vs-list-header icon="fa-info" icon-pack="fas" title="Information"/>
        <vs-list-item title="Name" :subtitle="name"/>
        <vs-list-item title="Description" :subtitle="description"/>
        <vs-list-header icon="fa-user-friends" icon-pack="fas" title="Developers"/>
        <vs-list-item 
          :key="index"
          v-for="(developer, index) in developers"
          :title="developer.username"
          :subtitle="developer.fullName"/>
      </vs-list>
    </vs-card>
    <Table header="Permission Groups" :data="groups" :fields="fields" :actions="actions" >
      <vs-button radius color="primary" type="filled" icon="fa-plus" icon-pack="fas" @click="newGroupActive = true"/>
    </Table>

    <vs-popup title="New permission group" :active.sync="newGroupActive">
      <div class="popup-form">
        <vs-input v-model="newGroupName" label="Name" />
        <vs-textarea v-model="newGroupDescription" label="Description" />
      </div>
      <vs-button @click="addPermissionGroup()" :disabled="!newGroupButton || !newGroupName || !newGroupDescription" type="gradient" icon="fa-plus" icon-pack="fas">
        Create
      </vs-button>
    </vs-popup>
  </div>
</template>

<script>
import Table from '@/components/Table.vue'

export default {
  name: "DevAppView",
  components: {
    Table
  },
  data() {
    return {
      name: "",
      description: "",
      token: "",
      rawDevelopers: [],
      groups: [],
      fields: [
        {
          title: "Name",
          value: "name"
        },
        {
          title: "Description",
          value: "description"
        }
      ],
      actions: [
        {
          icon: "fa-angle-right",
          color: "primary",
          to: (group) => "/dev/apps/" + this.$route.params.id + "/group/" + group.id
        }
      ],

      newGroupName: "",
      newGroupDescription: "",
      newGroupActive: false,
      newGroupButton: true
    }
  },
  computed: {
    developers() {
      return this.rawDevelopers.map(dev => {
        const {firstName, lastName} = dev;
        let fullName = "";
        if (firstName && lastName) fullName = firstName + " " + lastName;
        if (firstName || lastName) fullName = firstName || lastName;
        return {...dev, fullName};
       })
    }
  },

  methods: {
    getData() {
      const query = `
      {
        developerApps(id:${this.$route.params.id}) {
          name
          description
          token
          developers {
            username
            firstName
            lastName
          }

          groups {
            id
            name
            description
          }
        }
      }
      `
      this.$root.getData(query)
        .then(data => {
          if (data.developerApps.length == 0) {
            this.$root.notify("Application not found");
            this.$router.push("/dev/apps");
          } else {
            const { name, description, token, developers, groups} = data.developerApps[0];
            this.name = name;
            this.description = description;
            this.token = token;
            this.rawDevelopers = developers;
            this.groups = groups;
          }
        })
    },
    addPermissionGroup() {
      this.newGroupButton = false;

      const query = `
        mutation createPermissionGroup {
          createPermissionGroup(name: "${this.newGroupName}", description: "${this.newGroupDescription}", app: ${this.$route.params.id}) {
            ok,
            error
          }
        }
      `

      this.$store.dispatch("query", query)
        .then(resp => {
          if (resp.createPermissionGroup.ok) {
            this.$root.notify("success", "Permission group created successfully");
            this.newGroupActive = false;
            this.newGroupName = "";
            this.newGroupDescription = "";
          } else {
            this.$root.notify("fail", resp.createPermissionGroup.error);
          }
        })
        .catch(() => {
          this.$root.notify("fail", "Connection error");
        })
        .then(() => {
          this.getData();
          this.newGroupButton = true;
        });
    }
  },

  beforeMount() {
    this.getData();
  },
}
</script>

<style scoped>
#app-title {
  padding: 5px;
}

.data-table, .con-vs-card {
  margin-top: 20px;
}
</style>