<template>
  <div class="data-table">
    <vs-table stripe pagination max-items="10" :data="data">
      <template slot="header">
        <h3>
          {{ header }}
        </h3>
        <slot></slot>
      </template>
      <template slot="thead">
        <vs-th :key="index" v-for="(field, index) in fields" :sort-key="field.value">
          {{ field.title }}
        </vs-th>
        <vs-th v-if="actionsEnabled" :key="fields.length+1">
          Actions
        </vs-th>
      </template>
      <template slot-scope="{data}">
        <vs-tr :key="index" v-for="(dp, index) in data">
          <vs-td :key="index2" v-for="(field, index2) in fields" :data="dp[field.value]">
            {{dp[field.value]}}
          </vs-td>
          <vs-td v-if="actionsEnabled">
            <vs-button id="action-button" radius :key="index2" v-for="(action, index2) in actions" @click="action.callback(dp)" :color="action.color" type="flat" :icon="action.icon" icon-pack="fas" />
          </vs-td>
        </vs-tr>
      </template>
    </vs-table>
  </div>
</template>

<script>
export default {
  name: "Table",
  props: ["data", "header", "fields", "actions"],
  computed: {
    actionsEnabled() {
      return this.actions && this.actions.length > 0;
    } 
  }
}
</script>

<style lang="scss">
.content-tr-expand {
  justify-content: left;
}

.vs-list--item {
  width: 100%;
}

.header-table {
  padding: 10px;
}

.th-icon {
  font-size: .55rem !important;
}

#action-button {
  .vs-button--icon {
    font-size: smaller;
  }

  margin: 0;
  width: 20px !important;
  height: 2px !important;
}
</style>