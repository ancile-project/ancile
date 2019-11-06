<template>
  <div>
    <Table header="Applications" :data="addedApps" :fields="fields" :actions="actions">
      <vs-button radius color="primary" type="filled" icon="fa-plus" icon-pack="fas" @click="newAppActive = true"/>
    </Table>

    <vs-popup :title="currentApp.name" :active.sync="viewAppActive">
      <vs-row vs-justify="center">
        <vs-col type="flex" vs-justify="center" vs-align="center" vs-w="12">
          <vs-card :key="provider.id" v-for="provider in currentApp.providers">
            <div slot="header">
              <h3>
                {{ provider.displayName }}
              </h3>
            </div>
            <PolicyVisual v-for="policy in provider.policies" :key="policy.id" :policy="policy.value"/>
          </vs-card>
        </vs-col>
      </vs-row>
    </vs-popup>

    <vs-popup title="New application" :active.sync="newAppActive">
      <div class="popup-form">
        <vs-select class="inputx" label="Application" v-model="newApp">
          <vs-select-item :key="index" :value="app" :text="app.name" v-for="(app, index) in availableApps" />
        </vs-select>
        <vs-select v-if="newApp" class="inputx" label="Permission Group" v-model="newGroup">
          <vs-select-item :key="index" :value="group" :text="group.name" v-for="(group, index) in newApp.groups" />
        </vs-select>
        <vs-list v-if="newGroup">
          <div :key="id" v-for="(provider, id) in newGroup.providers">
            <vs-list-header icon-pack="fas" icon="fa-server" :title="provider.displayName"/>
            <vs-list-item title="Status" :subtitle="authButtonMessage(provider)" icon="fa-question" icon-pack="fas">
              <vs-button @click="authorize(provider)" :disabled="authorizedProviders[provider.id]" :color="authButtonColor(provider)" type="gradient" icon="fa-lock" icon-pack="fas">
                  Authorize
              </vs-button>
            </vs-list-item>
            <PolicyVisual v-for="policy in provider.policies" :key="policy.id" :policy="policy.value"/>
          </div>
        </vs-list>
        <div>
        <vs-button @click="addGroup()" :disabled="disabledaddAppButton" type="gradient" icon="fa-plus" icon-pack="fas">
          Add
        </vs-button>
        </div>
      </div>
    </vs-popup>
    </div>
</template>

<script>
import PolicyVisual from '@/components/PolicyVisual.vue'; 
import Table from '@/components/Table.vue';
import mermaid from 'mermaid';

export default {
  name: 'UserApps',
  components: {
    PolicyVisual,
    Table
  },
  data() {
    return {
      viewApp: {},
      viewAppActive: false,

      authorizedProviders: {},

      newApp: {},
      newGroup: {},
      newAppActive: false,
      addAppButton: false,
      authButtons: false,

      addedApps: [],
      availableApps: [],

      fields: [{
        title: "Name",
        value: "name"
      }],
  
      actions: [
        {
          color: "primary",
          icon: "fa-info",
          callback: (app) => {
            this.viewApp = app;
            this.viewAppActive = true;
          }
        },
        {
          color: "danger",
          icon: "fa-trash",
          callback: (app) => {
            let query = `
              mutation deleteApp($id: Int) {
                deleteApp(app: $id) {
                  ok
                }
              }
              `

              this.$root.getData(query, {id: app.id})
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
    disabledaddAppButton() {
      if (!this.newApp || !this.newGroup || this.addAppButton) return true;

      for (let provider in this.newGroup.providers) {
        if (authorizedProvder[provider.id]) return true;
      }
      return false;
    }
  },
  methods: {
    addGroup() {
      const group = this.apps[this.newApp].groups[this.newGroup].id;
      this.addAppButton = true;

      const query = `
        mutation addPermissionGroup {
          addPermissionGroup(app: $app, group: $group) {
            ok
          }
        }
      `

      const args = {
        app: this.newApp,
        group
      };

      this.newAppActive = false;
      this.$root.getData(query, args)
        .then(resp => {
          if (resp.addPermissionGroup.ok) {
            this.$root.notify("success", "Application added");
          } else {
            this.$root.notify("fail", "An error has occurred");
          }
          this.getData().then(() => {
            this.addAppButton = false;
          });
        });
    },

    authorize(provider) {
      let url = "/oauth/"

      this.authButtons = true;

      url += provider.pathName;
      let w = window.open(url);
      
      let refreshId =  setInterval(() => {
        if (w.closed) {
          this.authButtons = false;
          this.getData().then(() => {
              if (this.authorizedProviders[provider.id]) {
                return this.$root.notify("success", "Provider successfully added")
              }

              this.$root.notify("fail", "Provider authentication failed");
          });

          clearInterval(refreshId);
        }
      }, 1000);
    },

    async getData() {
      this.addedApps = {};
      this.availableApps = {};
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
            value
            provider {
              id
              displayName
              pathName
            }
          }
          groups {
            id
            name
            description
            policies {
              value
              provider {
                id
                displayName
                pathName
              }
            }
          }

        }
        allTokens {
          id,
          provider {
            id
          }
        }
      }
      `
    
    this.$root.getData(query)
      .then(resp => {

      resp.allTokens.forEach(token => {
        this.authorizedProviders[token.provider.id] = true;
      })

      resp.allApps = resp.allApps ? resp.allApps : [];

      resp.allApps.forEach(app => {
        if (app.policies && app.policies.length > 0) {
          this.addedApps.push(app);
        } else {
          this.availableApps.push(app);
        }
      });

    })
    },

    authButtonColor(provider) {
      return authorizedProviders[provider.id] ? "success" : "primary";
    },
    authButtonMessage(provider) {
      return authorizedProviders[provider.id] ? "Auhtorized" : "Not authorized";
    },
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