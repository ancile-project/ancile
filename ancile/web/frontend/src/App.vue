<template>
  <div id="app">
    <Sidebar ref="sidebar"/>
    <div id="left-padding">
      <Header />
      <div id="main">
        <transition name="fade" v-on:before-leave="updateIndex">
          <router-view></router-view>
        </transition>
      </div>
    </div>
    <Footer />
  </div>
</template>

<script>
import Footer from './components/Footer.vue'
import Header from './components/Header.vue'
import Sidebar from './components/Sidebar.vue'

import 'material-icons/iconfont/material-icons.css';
import 'typeface-open-sans'
import 'typeface-montserrat'
import '@fortawesome/fontawesome-free/css/fontawesome.css'
import '@fortawesome/fontawesome-free/css/regular.css'
import '@fortawesome/fontawesome-free/css/solid.css'

export default {
  name: 'app',
  components: {
    Footer,
    Header,
    Sidebar
  },
  mounted() {
    this.updateIndex();
  },
  methods: {
    updateIndex() {
      this.$refs.sidebar.refreshActive();
    }
  }
}
</script>

<style lang="scss">

#app {
  min-height: 100%;
}

#left-padding {
  margin-left: 54px;
  margin-right: 0px;
}

#main {
  margin-top: 20px;
  padding-bottom: 60px;
}

h1, h2, h3, h4 {
  font-family: 'Montserrat', sans-serif;
}

* {
  font-family: 'Open Sans', sans-serif;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity .5s;
  opacity: 0;
}

</style>
