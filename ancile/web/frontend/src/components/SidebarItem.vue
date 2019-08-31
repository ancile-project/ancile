<template>
  <vs-sidebar-item v-if="visible" ref="item" icon-pack="fas fa-fw" :index="index" :icon="icon" :to="to" :href="href">
    <span>{{ label }}</span>
  </vs-sidebar-item>
</template>

<script>
export default {
  name: "SidebarItem",
  props: {
    label: String,
    icon: String,
    index: Number,
    to: String,
    href: String,
    loggedIn: Number
  },
  computed: {
    visible: function() { return this.loggedIn === undefined || this.loggedIn == this.$root.loggedIn }
  },
  methods: {
    getActive: function() { return this.$parent.getActive() },
    setIndexActive: function(i) { return this.$parent.setIndexActive(i) },

    checkActive: function() {
      if (this.$el.children && this.$el.children[0].className.search("router-link-exact-active") > -1) {
        this.$children[0].setIndexActive();
      }
    }
  }
}
</script>

<style scoped>
span {
  margin-left: 24px;
}
</style>