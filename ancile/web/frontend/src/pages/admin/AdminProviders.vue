<template>
  <div id="user-providers">
    <Table :actions="actions" :data="providers" header="Providers" :fields="fields">
      <vs-button radius color="primary" type="filled" icon="fa-plus" icon-pack="fas" @click="addProviderPopup()"/>
    </Table>

    <vs-popup title="New provider" :active.sync="addProviderActive">
      <div class="popup-form">
        <vs-input v-model="currentProvider.displayName" label="Name" />
        <vs-input v-model="currentProvider.pathName" label="Path" />
        <vs-input v-model="currentProvider.clientId" label="Client ID" />
        <vs-input v-model="currentProvider.clientSecret" label="Client Secret" />
        <vs-input v-model="currentProvider.accessTokenUrl" label="Token URL" />
        <vs-input v-model="currentProvider.authUrl" label="Authorization URL" />
        <vs-button :disabled="!addProviderButton && !addProviderButtonActive" @click="addProvider()" color="primary" type="gradient" icon="fa-plus" icon-pack="fas">
          Add
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

    addProvider() {
      this.addProviderButtonActive = false;
      const query = `
        mutation addProvider($displayName: String,
                    $pathName: String,
                    $authUrl: String,
                    $accessTokenUrl: String,
                    $clientId: String,
                    $clientSecret: String,
                    $providerType: String)
          {
            addProvider(displayName: $displayName,
                        pathName: $pathName,
                        authUrl: $authUrl,
                        accessTokenUrl: $accessTokenUrl,
                        clientId: $clientId,
                        clientSecret: $clientSecret,
                        providerType: $providerType)
              {
                ok,
                error
              }
          }
      `

      const args = {...this.currentProvider, providerType: 'OAUTH'}
    

      this.$store.dispatch("query", { query, args })
        .then(resp => {
          if (resp.addProvider.ok) {
            this.$root.notify("success", "Provider created successfully.");
            this.addProviderActive = false;
            this.currentProvider = {};
          } else {
            this.$root.notify("fail", resp.addProvider.error);
          }
        })
        .catch(() => {
          this.$root.notify("fail", "Connection error.");
        })
        .then(() => {
          this.getData();
          this.addProviderButtonActive = true;
        });
    },

    addProviderPopup() {
      this.currentProvider = {}

      this.addProviderActive = true;
    },

    editProviderPopup(provider) {
      this.currentProvider = provider;
      this.addProviderActive = true;
    },

    deleteProvider(provider) {
      const query = ``;
      const args = {id: provider.id};

      this.$root.getData(query, args)
        .then(resp => {
          if (resp.deleteProvider.ok) {
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
          authUrl
          accessTokenUrl
          clientId
          clientSecret
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
      addProviderButtonActive: true,

      fields: [
        {
          "title": "Data Provider",
          "value": "displayName"
        }
      ],
      actions: [
        // {
        //   icon: "fa-edit",
        //   color: "primary",
        //   callback: this.editProviderPopup
        // },
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