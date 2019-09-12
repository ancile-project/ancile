<template>
  <div>
    <div>
      <h3>
        <router-link :to="'/dev/apps/' + $route.params.id"><vs-icon color="primary" icon-pack="fas" icon="fa-arrow-left"/></router-link>
        {{ $route.params.groupid }}
      </h3>
    </div>
  </div>
</template>

<script>
export default {
  name: "DevGroupView",
  data() {
    return {
      name: ""
    }
  }
}
</script>

<style>

</style>