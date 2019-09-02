<template>
  <vs-sidebar-item v-if="visible" ref="item" icon-pack="fas fa-fw" :index="index" :icon="icon" :to="to" :href="href">
    <span>{{ label }}</span>
  </vs-sidebar-item>
</template>

<script>
export default {
  name: "SidebarItem",
  data() {
    return {
      state: this.$root,
      test: true
    }
  },
  props: {
    label: String,
    icon: String,
    index: Number,
    to: String,
    href: String,
    inUser: {
      type: Boolean,
      default: false
    },
    inDeveloper: {
      type: Boolean,
      default: false
    },
    inAdmin: {
      type: Boolean,
      default: false
    },
    showAtLogout: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    visible: function() {
      const { inUser, inDeveloper, inAdmin, showAtLogout } = this;
      const { loggedIn, mode } = this.$store.state;

      if (loggedIn) {
        if (mode === "user") return inUser;
        if (mode === "dev") return inDeveloper;
        return inAdmin;
      }

      return showAtLogout || !(inAdmin || inUser || inDeveloper);
    }
  },
  methods: {
    getActive: function() { return this.$parent.getActive() },
    setIndexActive: function(i) { return this.$parent.setIndexActive(i) },

    checkActive: function() {
      const { path } = this.$router.currentRoute;
      if (path === this.to) {
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