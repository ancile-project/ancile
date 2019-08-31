<template>
  <div>
    <Table header="Applications" :data="userApps" :fields="fields" :actions="actions">
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
            <div v-html="policyGraph" :id='"mermaid" + providerId + "s" + index' :key="index" v-for="(policyGraph, index) in graphs[providerId]">
            </div>
          </vs-card>
        </vs-col>
      </vs-row>

    </vs-popup>
    <div id="mermaid">
    </div>
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
      apps: {},
      mermaid: mermaid.initialize({
        startOnLoad:false
    }),
      userApps: [],
      currentApp: "",
      viewAppActive: false,

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
                const id = "#mermaid" + i + "s" + index;
                console.log(id);
                console.log(graph);
                let theId = id.substring(1, id.length);
                console.log(document.getElementById(theId));
                setTimeout(()=>{
                console.log(theId);
                console.log(document.getElementById(theId));
                mermaid.render(id, graph, svg => { this.graphs[i][index] = svg; })
                });
              })
            }

          }
        }
      ]
    }
  },
  computed: {
  },
  methods: {
    getData() {
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
            name
            description
            scopes {
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
    
    this.$root.dataFetch(query, (resp) => {
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

      let apps = [];
      for (let id in this.apps) {
        if (Object.keys(this.apps[id].policies).length > 0) apps.push(this.apps[id]);
      }
      this.userApps = apps;
    })
    }
  },
  created() {
    this.getData()
  }
}
</script>

<style>

</style>