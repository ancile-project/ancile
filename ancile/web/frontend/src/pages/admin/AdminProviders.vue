<template>
  <div id="user-providers">
    <Table :actions="actions" :data="providers" header="Providers" :fields="fields">
      <vs-button radius color="primary" type="filled" icon="fa-plus" icon-pack="fas" @click="addProviderPopup()"/>
    </Table>

    <vs-popup title="New provider" :active.sync="addProviderActive">
      <div class="popup-form">
        <vs-input v-model="currentProvider.displayName" label="Name" />
        <vs-input v-model="currentProvider.pathName" label="Path" />
        <vs-input label="Client ID" />
        <vs-input label="Client Secret" />
        <vs-button :disabled="addProviderButton" @click="updateProvider()" color="primary" type="gradient" icon="fa-lock" icon-pack="fas">
          Authorize
        </vs-button>
      </div>
    </vs-popup>

  </div>
</template>

<script>
import Table from '../../components/Table.vue'

export default {
  name: "AdminProviders",

  components: {
    Table
  },

  methods: {

    updateProvider() {

    },

    addProviderPopup() {
      this.currentProvider = {
        id: -1,
        displayName: "",
        pathName: ""
      }

      this.addProviderActive = true;
    },

    editProviderPopup(provider) {
      this.currentProvider = provider;
      this.addProviderActive = true;
    },

    deleteProvider(provider) {
      const query = ``

      const args = {
        id: provider.id
      };

      this.$root.getData(query, args)
        .then(resp => {
          if (resp.deleteToken.ok) {
            this.$root.notify("success", "Provider removed");
          } else {
            this.$root.notify("fail", "An error has occurred");
          }
          this.getData();
        });
    },
    
    addScope(scope) {
      this.allSelectedScopes = [...this.allSelectedScopes, scope];
    },
    removeScope(scope) {
      this.allSelectedScopes = this.allSelectedScopes.filter(s => scope !== s);
    },

    async getData() {
      this.allProviders = [];

      const query = 
    `
      {
        allProviders {
          id
          displayName
          pathName
          scopes {
            id
            value
            simpleName
            description
          }
        }
      }
    `
    const data = await this.$root.getData(query);
    this.providers = data.allProviders;
    },
  },
  
  computed: {
    addProviderButton() {
      return this.currentProvider.pathName && this.currentProvider.displayName;
    },

    scopePickerLabel() {
      if (this.newProvider) {
        if (this.selectedScopes.length) {
          return "No scopes left"
        }
        return "No scopes available for this provider"
      }
      return "Please select a provider"
    },

  },

  data() {
    return {  
      providers: [],
      currentProvider: {},
      addProviderActive: false,

      fields: [
        {
          "title": "Data Provider",
          "value": "displayName"
        }
      ],
      actions: [
        {
          icon: "fa-edit",
          color: "primary",
          callback: this.editProviderPopup
        },
        {
          icon: "fa-trash",
          color: "danger",
          callback: this.deleteProvider
        },
      ]
    }
  },
  created() {
    this.getData();
  }
}
</script>

<style>
</style>