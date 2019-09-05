<template>
  <codeEditor id="editor" v-model="code" @init="editorInit" :lang="lang" :theme="theme" :width="width" :height="height"/>
</template>

<script>
export default {
  name: "Editor",
  props: ["value","width", "height", "theme", "lang"],
  components: {
    codeEditor: require('vue2-ace-editor'),
  },

  computed: {
    code: {
      get() {
        return this.value;
      },

      set(c) {
        this.$emit('input', c);
      }
    }
  },
  methods: {
    editorInit() {
      require('brace/mode/python');
      require('brace/theme/tomorrow');
    }
  }
}
</script>

<style>
#editor {
  font-family: monospace !important;
  border-radius: 5px;
}
</style>