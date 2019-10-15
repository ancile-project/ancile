<template>
  <div>
      <div>
        <h3>
          <router-link to="/dev/apps/"><vs-icon color="primary" icon-pack="fas" icon="fa-arrow-left"/></router-link>
          {{ app.name }}
        </h3>
      </div>

    <vs-card>
      <vs-list>
        <vs-list-header icon="fa-info" icon-pack="fas" title="Information"/>
        <vs-list-item title="Name" :subtitle="app.name"/>
        <vs-list-item title="Description" :subtitle="app.description"/>
        <vs-list-header icon="fa-user-friends" icon-pack="fas" title="Developers"/>
        <vs-list-item 
          :key="index"
          v-for="(developer, index) in developers"
          :title="developer.username"
          :subtitle="developer.fullName"/>
        <vs-list-header icon="fa-user-lock" icon-pack="fas" title="Token"/>
        <vs-list-item class="token" :title="app.token"/>
      </vs-list>
    </vs-card>

    <vs-card>
      <div slot="header" class="policy-group-header">
        <h2>
        Policy Groups  
        </h2>
        <vs-button v-if="adminMode" radius color="primary" type="filled" icon="fa-plus" icon-pack="fas" @click="newGroupActive = true"/>
      </div>
      <vs-list :key="index" v-for="(group, index) in app.groups">
        <vs-list-header icon="fa-info" color="success" icon-pack="fas" :title="group.name"/>
        <vs-list-item :title="group-description"/>
        <vs-list-item title="Example Policy" subtitle="Example description" >
          <vs-button color="primary" icon="fa-eye" icon-pack="fas">
            View
          </vs-button>
          <vs-button v-if="adminMode" color="primary" icon="fa-eye" icon-pack="fas">
            Edit
          </vs-button>
          <vs-button v-if="adminMode" color="red" icon="fa-eye" icon-pack="fas">
            Delete
          </vs-button>
        </vs-list-item>
      </vs-list>
    </vs-card>

    <vs-popup v-if="adminMode" title="New permission group" :active.sync="newGroupActive">
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
export default {
  name: "AppView",
  props: {
    adminMode: {
      type: Boolean,
      default: false
    },
  },
  data() {
    return {
      app: {
        name: "",
        description: "",
        token: "",
        developers: [],
        groups: [],
      },

      newGroupName: "",
      newGroupDescription: "",
      newGroupActive: false,
      newGroupButton: true
    }
  },
  computed: {
    developers() {
      return this.app.developers.map(dev => {
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
      query($id: Int) {
        developerApps(id:$id) {
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

      const args = {
        id: this.$route.params.id
      }
      this.$root.getData(query, args)
        .then(data => {
          if (data.developerApps.length == 0) {
            this.$root.notify("Application not found");
            this.$router.push("/dev/apps");
          } else {
            this.app = data.developerApps[0];
          }
        })
    },
    addPermissionGroup() {
      this.newGroupButton = false;

      const query = `
        mutation createPermissionGroup($newGroupName: String, $newGroupDescription: String, $id: Int) {
          createPermissionGroup(name: $newGroupName, description: $newGroupDescription, app: $id) {
            ok,
            error
          }
        }
      `

      const args = {
        newGroupName: this.newGroupName,
        newGroupDescription: this.newGroupDescription,
        id: this.$route.params.id
      };

      this.$store.dispatch("query", { query, args })
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

<style lang="scss">
#app-title {
  padding: 5px;
}

.data-table, .con-vs-card {
  margin-top: 20px;
}

.list-titles {
  overflow: hidden;

  .vs-list--title, .vs-list--subtitle {
    word-wrap: break-word;
  }

}

.vs-list--slot .vs-button {
  margin-left: 0.25rem;
}

.policy-group-header {
  display: flex;
  justify-content: space-between;
  margin: 0 0.5rem;
  align-items: center;
}
</style>