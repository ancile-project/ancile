<template>
  <div id="user-providers">
    <Table :data="providers" header="Providers" :fields="fields">
    <vs-button radius color="primary" type="filled" icon="fa-plus" icon-pack="fas" @click="popupActive = true"/>
    </Table>

    <vs-popup title="Add Provider" :active.sync="popupActive">
      <vs-select class="inputx" v-model="newProvider">
        <vs-select-item :key="index" :value="item.value" :text="item.name" v-for="(item, index) in availableProviders" />
      </vs-select>
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
  
  computed: {
    providers() {
      let providers = [];
      let used = {};

      for (let id in this.allTokens) {
        let token = this.allTokens[id];
        used[token.provider.id] = true;

        providers.push({
          name: this.allProviders[token.provider.id].displayName,
          expiry: new Date(token.expiresAt * 1000).toUTCString()
        })
      }

      let open = [];

      for (let id in this.allProviders) {
        if (!used[id]) {
          open.push({
            name: this.allProviders[id].displayName,
            value: id
          })
        }
      }
      
      this.availableProviders = open;

      return providers;
    },

  },

  data() {
    return {
      popupActive: false,
      availableProviders: {},
      newProvider: "",
      allProviders: {},
      allTokens: {},
      allScopes: {},
      fields: [
        {
          "title": "Data Provider",
          "value": "name"
        },
        {
          "title": "Expiry Date",
          "value": "expiry"
        },
        
      ]
    }
  },

  created() {
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
      this.allScopes = this.$root.listToObject(data.allScopes)
    })

  }
}
</script>

<style>

</style>