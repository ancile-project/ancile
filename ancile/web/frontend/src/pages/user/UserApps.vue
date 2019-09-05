<template>
  <div>
    <Table header="Applications" :data="userApps" :fields="fields" :actions="actions">
      <vs-button radius color="primary" type="filled" icon="fa-plus" icon-pack="fas" @click="newAppActive = true"/>
    </Table>

    <vs-popup v-if="currentApp" :title="currentApp.name" :active.sync="viewAppActive">
      <vs-row vs-justify="center">
        <vs-col type="flex" vs-justify="center" vs-align="center" vs-w="12">
          <vs-card :key="providerId" v-for="providerId in Object.keys(currentApp.policies)">
            <div slot="header">
              <h3>
                {{ providers[providerId].displayName }}
              </h3>
            </div>
            <div v-if="viewAppActive">
              <div class="mermaid" v-html="policyGraph" :id='"mermaid" + providerId + "s" + index' :key="policyGraph" v-for="(policyGraph, index) in graphs[providerId]">
              </div>
            </div>
          </vs-card>
        </vs-col>
      </vs-row>
    </vs-popup>
    
    <vs-popup title="New application" :active.sync="newAppActive">
      <div class="popup-form">
        <vs-select class="inputx" label="Application" v-model="newApp">
          <vs-select-item :key="index" :value="app.id" :text="app.name" v-for="(app, index) in availableApps" />
        </vs-select>
        <vs-select v-if="newApp" class="inputx" label="Permission Group" v-model="newGroup">
          <vs-select-item :key="index" :value="index" :text="group.name" v-for="(group, index) in apps[newApp].groups" />
        </vs-select>
        <vs-list v-if="newGroup >= 0">
          <div :key="id" v-for="(scopes, id) in apps[newApp].groups[newGroup].scopes">
            <vs-list-header icon-pack="fas" icon="fa-server" :title="providers[id].displayName"/>
            <vs-list-item :key="index" v-for="(scope, index) in scopes" icon-pack="fas" icon="fa-lock" :title="scope.simpleName" :subtitle="scope.description"></vs-list-item>
            <vs-list-item title="Status" :subtitle="authButtonMessage(providers[id],scopes)" icon="fa-question" icon-pack="fas">
              <vs-button @click="authorize(providers[id], scopes)" :disabled="authButtons || providers[id].authorized" :color="authButtonColor(providers[id], scopes)" type="gradient" icon="fa-lock" icon-pack="fas">
                  Authorize
              </vs-button>
            </vs-list-item>
          </div>
        </vs-list>
        <div>
        <vs-button @click="addGroup()" :disabled="disabledAddGroupButton" type="gradient" icon="fa-plus" icon-pack="fas">
          Add
        </vs-button>
        </div>
      </div>
    </vs-popup>
    </div>
</template>

<script>
import Table from '../../components/Table.vue';
import mermaid from 'mermaid';

export default {
  name: 'UserApps',
  components: {
    Table
  },
  data() {
    return {
      appKey: 0,
      apps: {},
      userApps: [],
      availableApps: [],
      currentApp: "",
      viewAppActive: false,
      authButtons: false,

      addGroupButton: false,
      newApp: "",
      newGroup: -1,
      newAppActive: false,

      graphs: {},

      providers: {},
      fields: [{
        title: "Name",
        value: "name"
      }],
      actions: [
        {
          color: "primary",
          icon: "fa-info",
          callback: (app) => {

            this.graphs = {};
            for (let i in app.policies) {
              this.graphs[i] = app.policies[i].map(e => e);
            }

            this.currentApp = app;
            this.viewAppActive = true;


            for (let i in app.policies) {
              app.policies[i].forEach((graph, index) => {
                const id = "mermaid" + i + "s" + index;
                mermaid.render(id, graph, svg => this.graphs[i][index] = svg)
              })
            }

          }
        },
        {
          color: "danger",
          icon: "fa-trash",
          callback: (app) => {
            let query = `
              mutation deleteApp {
                deleteApp(app: ${app.id}) {
                  ok
                }
              }
              `
              this.$root.getData(query)
                .then(resp => {
                  if (resp.deleteApp.ok) {
                    this.$root.notify("success", "Application deleted.");
                  } else {
                    this.$root.notify("fail", "An error has occurred");
                  }
                  this.getData();
                });
          }
        }
      ]
    }
  },
  computed: {
    disabledAddGroupButton() {
      if (!this.newApp || this.newGroup) return true;
      const group = this.apps[this.newApp].groups[this.newGroup];

      for (let providerId in group.scopes) {
        const provider = this.providers[providerId];
        if (!provider.authorized || !this.satifiesScopes(provider, group.scopes[providerId])) return true;
      }
      return false || this.addGroupButton;
    }
  },
  methods: {
    addGroup() {
      const group = this.apps[this.newApp].groups[this.newGroup].id;
      this.addGroupButton = true;

      const query = `
        mutation addPermissionGroup {
          addPermissionGroup(app: ${this.newApp}, group: ${group}) {
            ok
          }
        }
      `
      this.newAppActive = false;
      this.$root.getData(query)
        .then(resp => {
          if (resp.addPermissionGroup.ok) {
            this.$root.notify("success", "Application added");
          } else {
            this.$root.notify("fail", "An error has occurred");
          }
          this.getData(() => {
            this.addGroupButton = false;
          });
        });
    },
    authorize(provider, scopes) {
      let url = "/oauth/"

      this.authButtons = true;

      url += provider.pathName;
      url += "?scopes=" + scopes.map(scope => scope.value).join(" ");
      let w = window.open(url);
      
      let refreshId =  setInterval(() => {
        if (w.closed) {
          this.authButtons = false;
          this.getData(() => {
              if (this.providers[provider.id].scopes.length > 0) {
                return this.$root.notify("success", "Provider successfully added")
              }

              this.$root.notify("fail", "Provider authentication failed")
          });

          clearInterval(refreshId);
        }
      }, 1000);
    },
    getData(callback) {
      this.providers = {};
      this.apps = {};
      this.currentApp = "";
      this.newApp = "";
      this.newGroup = -1;

      let query = `
      {
        allApps {
          id
          name
          description
          policies {
            graph
            provider {
              id
            }
          }
          groups {
            id
            name
            description
            scopes {
              id
              simpleName
              value
              provider {
                id
              }
            }
          }

        }
        allProviders {
          id
          displayName
          pathName
        },
        allTokens {
          id,
          scopes {
            id
          }
          provider {
            id
          }
        }
      }
      `
    
    this.$root.getData(query)
      .then(resp => {
        resp.allProviders.forEach(provider => {
          this.providers[provider.id] = provider;
        })

      resp.allTokens.forEach(token => {
        this.providers[token.provider.id].authorized = true;
        this.providers[token.provider.id].scopes = token.scopes.map(scope => scope.id);
      })

      resp.allApps = resp.allApps ? resp.allApps : [];

      resp.allApps.forEach(app => {
        this.apps[app.id] = app;
        if (app.policies) {
          let newPolicies = {}
          app.policies.forEach(policy => {
            if (!newPolicies[policy.provider.id]) newPolicies[policy.provider.id] = [];
              newPolicies[policy.provider.id].push(policy.graph);
          })
          app.policies = newPolicies;
        }
        if (app.groups) app.groups.forEach(group => {
          let newScopes = {};
          group.scopes.forEach(scope => {
            if (!newScopes[scope.provider.id]) newScopes[scope.provider.id] = [];

            newScopes[scope.provider.id].push(scope);
          })
          group.scopes = newScopes;
        })
      })

      this.userApps = [];
      this.availableApps = [];
      for (let id in this.apps) {
        if (Object.keys(this.apps[id].policies).length > 0) {
          this.userApps.push(this.apps[id]);
        } else {
          this.availableApps.push(this.apps[id]);
        }
      }

      callback ? callback() : null;
    })
    },
    authButtonColor(provider, scopes) {
      if (!provider.authorized) return "primary";
      return this.satifiesScopes(provider, scopes) ? "success" : "warning";
    },
    authButtonMessage(provider, scopes) {
      if (!provider.authorized) return "Not authorized";
      return this.satifiesScopes(provider, scopes) ? "Authorized with correct scopes" : "Authorized with insufficient scopes";
    },
    satifiesScopes(provider, scopes) {
      return scopes.reduce((prev, scope) => prev && provider.scopes.includes(scope.id), true);
    }
  },
  created() {
    this.getData()
  }
}
</script>

<style>
g > .path {
 -webkit-animation: none !important;
 animation: none !important;
}

.mermaid {
  text-align: center;
}
</style>