<template>
  <div id="user-providers">
    <Table :actions="actions" :data="providers" header="Providers" :fields="fields">
      <vs-button radius color="primary" type="filled" icon="fa-plus" icon-pack="fas" @click="popupActive = true"/>
    </Table>

    <vs-popup title="Add Provider" :active.sync="popupActive">
      <div class="popup-form">
        <vs-select class="inputx" label="Provider" v-model="newProvider" @change="updateScopes()">
          <vs-select-item :key="index" :value="item.value" :text="item.name" v-for="(item, index) in availableProviders" />
        </vs-select>
        <div class="vs-select--label">
          Available scopes
        </div>
        <vs-chips color="rgb(145, 32, 159)" :placeholder="scopePickerLabel" v-model="unusedScopes" @change="validateScopes()" remove-icon="add">
          <vs-chip :key="index" @click="addScope(scope)" v-for="(scope, index) in unusedScopes" closable close-icon="add">
            {{ scope.simpleName }}
          </vs-chip>
        </vs-chips>

        <div class="vs-select--label">
          Selected scopes
        </div>
        <vs-chips color="rgb(145, 32, 159)" placeholder="No scopes chosen." v-model="usedScopes" remove-icon="delete_forever">
          <vs-chip :key="index" @click="removeScope(scope)" v-for="(scope, index) in usedScopes" closable close-icon="delete">
            {{ scope.simpleName }}
          </vs-chip>
        </vs-chips>

        <vs-button :disabled="buttonDisabled" @click="authorize()" color="primary" type="gradient" icon="fa-lock" icon-pack="fas">
          Authorize
        </vs-button>
      </div>
    </vs-popup>

    <vs-popup :title="currentToken.provider" :active.sync="viewProviderActive">
      <h3>
        Scopes
      </h3>   
      <vs-list v-if="currentToken">
        <vs-list-item :key="index" v-for="(scope, index) in currentToken.scopes" :title="scope.simpleName" :subtitle="scope.description"></vs-list-item>
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
      this.unusedScopes = this.unusedScopes.filter(s => scope !== s);
      this.usedScopes = [...this.usedScopes, scope];
    },
    removeScope(scope) {
      this.usedScopes = this.unusedScopes.filter(s => scope !== s);
      this.unusedScopes = [...this.usedScopes, scope];
    },
    updateScopes() {
      if (this.newProvider) {
        this.unusedScopes = this.allProviders[this.newProvider].scopes.map(scope => this.allScopes[scope.id]);
        this.usedScopes = [];
        this.buttonDisabled = false;
      } else {
        this.unusedScopes = [];
        this.usedScopes = [];
        this.buttonDisabled = true;
      }
      
    },
    authorize() {
      let url = "/oauth/"

      if (this.newProvider) {
        this.buttonDisabled = true;
        let provider = this.allProviders[this.newProvider];

        url += provider.pathName;
        url += "?scopes=" + this.usedScopes.map(scope => scope.value).join(" ");
        let w = window.open(url);
        
        let refreshId =  setInterval(() => {
          if (w.closed) {
            this.buttonDisabled = false;
            this.popupActive = false;
            this.getData(() => {
              for (let i in this.allTokens) {
                if (this.allTokens[i].provider.id === provider.id) {
                  return this.$root.notify("success", "Provider successfully added")
                }

                this.$root.notify("fail", "Provider authentication failed")
              }
            });

            clearInterval(refreshId);
          }
        }, 1000);
      }
    },

    getData(callback) {
      this.allProviders = {};
      this.allTokens = {};
      this.allScopes = {};

      const query = 
    `
      {
        allTokens {
          id
          expiresAt
          provider {
            id
          }
          scopes {
            id
          }
        }
        allProviders {
          id
          displayName
          pathName
          scopes {
            id
          }
        }
        allScopes {
          id
          value
          simpleName
        }
      }
    `

    this.$root.dataFetch(query, data => {
      this.allProviders = this.$root.listToObject(data.allProviders);
      this.allTokens = this.$root.listToObject(data.allTokens);
      this.allScopes = this.$root.listToObject(data.allScopes);

      if (callback) callback();
    });
    }

  },
  
  computed: {
    providers() {
      let providers = [];
      let used = {};

      for (let id in this.allTokens) {
        let token = this.allTokens[id];
        used[token.provider.id] = true;

        providers.push({
          name: this.allProviders[token.provider.id].displayName,
          expiry: new Date(token.expiresAt * 1000).toUTCString(),
          id: id
        })
      }

      return providers;
    },

    availableProviders() {
      let available = [];
      let unavailable = {}

      this.providers.forEach(prov => unavailable[prov.id] = true);
  
      for (let id in this.allProviders) {
        if (!unavailable[id]) {
          available.push({
            name: this.allProviders[id].displayName,
            value: id
          })
        }
      }

      return available;
    },

    scopePickerLabel() {
      if (this.newProvider) {
        if (this.usedScopes.length) {
          return "No scopes left"
        }
        return "No scopes available for this provider"
      }
      return "Please select a provider"
    },

  },

  data() {
    return {
      buttonDisabled: true,
      popupActive: false,
      unusedScopes: [],
      usedScopes: [],
      newProvider: "",
      allProviders: {},
      allTokens: {},
      allScopes: {},
      currentToken: false,
      viewProviderActive: false,
      fields: [
        {
          "title": "Data Provider",
          "value": "name"
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
          callback: (tr) => {
            let token = this.allTokens[tr.id];

            this.currentToken = {
              provider: this.allProviders[token.provider.id].displayName,
              scopes: token.scopes.map(scope => this.allScopes[scope.id])
            }
            this.viewProviderActive = true;
          }
        },
        {
          icon: "fa-trash",
          color: "danger",
          callback: (tr) => {
            let query = `
            mutation deleteToken {
              deleteToken(token: ${tr.id}) {
                ok
              }
            }
            `
            this.$root.dataFetch(query, resp => {
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
  margin: 10px;
}

input[type="text"]:disabled {
  background-color: white;
}

.con-chips--remove-all {
  display: none !important;
}
</style>