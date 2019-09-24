<template>
    <div>
      <Table header="Applications" :data="apps" :fields="fields" :actions="actions">
        <vs-button radius color="primary" type="filled" icon="fa-plus" icon-pack="fas" @click="newAppActive = true"/>
      </Table>

      <vs-popup title="New application" :active.sync="newAppActive">
        <div class="popup-form">
          <vs-input v-model="newAppName" label="Name" />
          <vs-textarea v-model="newAppDescription" label="Description" />
        </div>
        <vs-button @click="addApp()" :disabled="!newAppButton || !newAppName" type="gradient" icon="fa-plus" icon-pack="fas">
          Create
        </vs-button>
      </vs-popup>
    </div>
</template>

<script>
import Table from '@/components/Table.vue';

export default {
  name: "DevAppsTable",

  components: {
    Table
  },

  data() {
    return {
      apps: [],
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
          to: (app) => "/dev/apps/" + app.id
        }
      ],


      newAppName: "",
      newAppDescription: "",
      newAppActive: false,
      newAppButton: true,
    }
  },

  methods: {
    getData() {
      const query = `
        {
          developerApps {
            id,
            name,
            description
          }
        }
      `

      this.$root.getData(query)
        .then(data => this.apps = data.developerApps);
    },

    addApp() {
      this.newAppButton = false;

      const query = `
        mutation addApp {
          addApp(name: "${this.newAppName}", description: "${this.newAppDescription}") {
            ok,
            error
          }
        }
      `

      this.$store.dispatch("query", query)
        .then(resp => {
          if (resp.addApp.ok) {
            this.$root.notify("success", "App created successfully.");
            this.newAppActive = false;
            this.newAppName = "";
            this.newAppDescription = "";
          } else {
            this.$root.notify("fail", resp.addApp.error);
          }
        })
        .catch(() => {
          this.$root.notify("fail", "Connection error.");
        })
        .then(() => {
          this.getData();
          this.newAppButton = true;
        });
    }
  },

  created() {
    this.getData();
  }
}
</script>

<style>

</style>