
<template>
  <vs-input v-model="fieldValue" :danger="error ? true : false" :danger-text="error" :type="type" :placeholder="placeholder" val-icon-danger="close"/>
</template>

<script>
export default {
  name: "Input",
  props: {
    value: {
      default: "",
      type: [String, Number]
    },
    error: {
      default: "",
      type: [String]
    },
    type: {
      default: "",
      type: [String]
    },
    placeholder: {
      default: "",
      type: [String, Number]
    }
  },
  computed: {
    fieldValue: {
      get() {
        return this.value;
      },

      set(value) {
        this.$emit("input", value);
      }
    }
  } 
}
</script>

<style>

</style>