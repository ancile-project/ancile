<template>
  <div class="data-table">
    <vs-table stripe :data="data">
      <template slot="header">
        <h3>
          {{ header }}
        </h3>
        <slot></slot>
      </template>
      <template slot="thead">
        <vs-th :key="index" v-for="(tr, index) in fields" :sort-key="fields[index].value">
          {{ fields[index].title }}
        </vs-th>
      </template>
      <template slot-scope="{data}">
        <vs-tr :key="index" v-for="(tr, index) in data">
          <vs-td :key="index2" v-for="(tr, index2) in fields" :data="data[index][fields[index2].value]">
            {{data[index][fields[index2].value]}}
          </vs-td>
        </vs-tr>
      </template>
    </vs-table>
  </div>
</template>

<script>
export default {
  name: "Table",
  props: ["data", "header", "fields"]
}
</script>

<style>
.data-table {
  margin: 20px;
}

.header-table {
  padding: 10px;
}

.th-icon {
  font-size: .55rem !important;
}
</style>