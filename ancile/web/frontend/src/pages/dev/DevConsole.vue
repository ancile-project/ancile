<template>
  <vs-card>
    <div slot="header">
      <h3>Console</h3>
    </div>
    <div id="card-body">
      <vs-select
        label="Application:"
        v-model="app"
        width="100%"
        >
        <vs-select-item :key="index" :value="app.id" :text="app.name" v-for="(app,index) in apps" />
      </vs-select>
      <div>
        <label class="vs-select--label">Users:</label>
        <vs-chips color="rgb(145, 32, 159)" placeholder="Users" v-model="users">
          <vs-chip
            :key="user"
            @click="remove(user)"
            v-for="user in users" closable>
            <vs-avatar />
            {{ user }}
          </vs-chip>
        </vs-chips>
      </div>
      <div>
        <vs-row
        vs-align="flex-start"
        vs-type="flex" vs-justify="space-between" vs-w="12">
          <vs-col item.textvs-type="flex" vs-justify="center" vs-align="center" vs-w="6">
              <label class="vs-select--label">Program:</label>
          </vs-col>
          <vs-col item.textvs-type="flex" vs-justify="center" vs-align="center" vs-w="5">
              <label class="vs-select--label">Output:</label>
          </vs-col>
        </vs-row>
        <vs-row
        vs-align="flex-start"
        vs-type="flex" vs-justify="space-between" vs-w="12">
          <vs-col item.textvs-type="flex" vs-justify="center" vs-align="center" vs-w="6">
            <Editor v-model="code" lang="python" theme="tomorrow" width="100%" height="500px"/>
          </vs-col>
          <vs-col vs-type="flex" vs-justify="center" vs-align="center" vs-w="5">
            <vs-textarea :value="output" width="100%" style="height:500px" >
            </vs-textarea>
          </vs-col>
        </vs-row>
      </div>
      <vs-row vs-align="flex-start"
      vs-type="flex" vs-justify="space-around" vs-w="12">
        <vs-col vs-type="flex" vs-justify="center" vs-align="center" vs-w="12">
          <vs-button :disabled="!runButton" @click="execute()" color="primary" icon="fa-play" icon-pack="fas">Run</vs-button>
        </vs-col>
      </vs-row>
    </div>
  </vs-card>
</template>

<script>
import Editor from '@/components/Editor.vue'
export default {
  name: "DevConsole",
  data() {
    return {
      code: "",
      output: "",
      users: [],
      apps: [],
      app: -1,
      runButton: true,
    }
  },

  components: {
    Editor
  },
  methods: {
    remove(user) {
      this.users = this.users.filter(u => u !== user);
    },

    getData() {
      const query = `
        {
          developerApps {
            name
            id
          }
        }
      `

      this.$root.getData(query)
        .then(resp => {
          this.apps = resp.developerApps;
        })
    },

    execute() {
      const payload = {
        app_id: this.app,
        users: this.users,
        program: this.code
      }

      this.runButton = false;

      this.$store.dispatch("post", {
        endpoint: "/api/browser_run",
        data: payload
      })
      .then(resp => {
        this.output = JSON.stringify(resp.data);
        this.runButton = true;
      })
      .catch(() => {
        this.$root.notify("fail", "Connection error.")
      })
    }
  },

  created() {
    this.getData();
  }
}
</script>

<style scoped>
#card-body > * {
  margin: 10px 0;
}

.vs-select--label {
  margin-bottom: 5px;
}
</style>