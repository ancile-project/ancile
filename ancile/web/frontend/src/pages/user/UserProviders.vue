<template>
  <div id="user-providers">
    <Table :actions="actions" :data="authenticatedProviders" header="Providers" :fields="fields">
      <vs-button radius color="primary" type="filled" icon="fa-plus" icon-pack="fas" @click="addProviderActive = true"/>
    </Table>

    <vs-popup title="New provider" :active.sync="addProviderActive">
      <div class="popup-form">
        <vs-select class="inputx" label="Provider" v-model="newProvider">
          <vs-select-item :key="index" :value="provider" :text="provider.displayName" v-for="(provider, index) in availableProviders" />
        </vs-select>
        <div>
          <div class="vs-select--label">
            Available scopes
          </div>
          <vs-chips class="no-icon" color="rgb(145, 32, 159)" :placeholder="scopePickerLabel" v-model="nonSelectedScopes">
            <vs-chip :key="index" @click="addScope(scope)" v-for="(scope, index) in nonSelectedScopes" closable close-icon="add">
              {{ scope.simpleName }}
            </vs-chip>
          </vs-chips>

          <div class="vs-select--label">
            Selected scopes
          </div>
          <vs-chips class="no-icon" color="rgb(145, 32, 159)" placeholder="No scopes chosen." v-model="selectedScopes">
            <vs-chip :key="index" @click="removeScope(scope)" v-for="(scope, index) in selectedScopes" closable close-icon="delete">
              {{ scope.simpleName }}
            </vs-chip>
          </vs-chips>
        </div>

        <vs-button :disabled="!addProviderButton || !newProvider.id" @click="authorize()" color="primary" type="gradient" icon="fa-lock" icon-pack="fas">
          Authorize
        </vs-button>
      </div>
    </vs-popup>

    <vs-popup :title="currentProvider.displayName" :active.sync="viewProviderActive">
      <h3>
        Scopes
      </h3>   
      <vs-list v-if="currentProvider.id">
        <vs-list-item icon-pack="fas" icon="fa-lock" :key="index" v-for="(scope, index) in currentProvider.token.scopes" :title="scope.simpleName" :subtitle="scope.description"></vs-list-item>
      </vs-list>
    </vs-popup>
  </div>
</template>

<script>
import Table from '../../components/Table.vue'

export default {
  name: "UserProviders",

  components: {
    Table
  },

  methods: {
    addScope(scope) {
      this.allSelectedScopes = [...this.allSelectedScopes, scope];
    },
    removeScope(scope) {
      this.allSelectedScopes = this.allSelectedScopes.filter(s => scope !== s);
    },

    authorize() {
      const { id } = this.newProvider;
      this.addProviderButton = false;
      this.$root.oauth(this.newProvider, this.selectedScopes.map(scope => scope.value))
        .then(() => {
          this.addProviderButton = true;
          this.addProviderActive = false;

          this.getData()
            .then(() => {
              if (this.authenticatedProviders.reduce((prev, provider) => prev || (provider.id === id), false)) {
                this.$root.notify("success", "Successfully authorized");
              } else {
                this.$root.notify("fail", "Authorization failed");
              }
            })
        });
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
          token {
            id
            expiresAt
            scopes {
              id
              value
              simpleName
              description
            }
          }
        }
      }
    `
    const data = await this.$root.getData(query);
    this.allProviders = data.allProviders;
    },
  },
  
  computed: {
    authenticatedProviders() {
      return this.allProviders
        .filter(provider => provider.token)
        .map(provider => ({...provider, expiry: new Date(provider.token.expiresAt * 1000).toUTCString()}));
    },

    availableProviders() {
      return this.allProviders
        .filter(provider => !provider.token);
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

    nonSelectedScopes() {
      return !this.newProvider.id ? [] : this.newProvider.scopes.filter(s => !this.selectedScopes.includes(s));
    },

    selectedScopes: {
      get() {
        return this.allSelectedScopes.filter(scope => this.newProvider.scopes.includes(scope));
      }
    }

  },

  data() {
    return {
      addProviderButton: true,
      addProviderActive: false,

      allSelectedScopes: [],
  
      newProvider: {},
      allProviders: [],

      currentProvider: {},
      viewProviderActive: false,

      fields: [
        {
          "title": "Data Provider",
          "value": "displayName"
        },
        {
          "title": "Expiry Date",
          "value": "expiry"
        },
        
      ],
      actions: [
        {
          icon: "fa-info",
          color: "primary",
          callback: (provider) => {
            this.currentProvider = provider;
            this.viewProviderActive = true;
          }
        },
        {
          icon: "fa-trash",
          color: "danger",
          callback: (provider) => {
            const query = `
            mutation deleteToken {
              deleteToken(token: $id {
                ok
              }
            }
            `

            const args = {
              id: provider.token.id
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
          }
        },
      ]
    }
  },
  mounted() {
    Array.prototype.forEach.call(document.getElementsByClassName("con-chips--input"), el => {
      el.disabled = true;
    });
  },
  created() {
    this.getData();
  }
}
</script>

<style>
.popup-form > * {
  margin: 10px 0;
}

input[type="text"]:disabled {
  background-color: white;
}

.no-icon > .con-chips > .con-chips--remove-all {
  display: none !important;
}
</style>