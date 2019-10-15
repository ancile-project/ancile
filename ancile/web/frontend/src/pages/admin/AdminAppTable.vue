<template>
    <AppTable :adminMode="true" />
</template>

<script>
import AppTable from '@/components/AppTable.vue';

export default {
  name: "AdminAppTable",
  components: {
    AppTable
  },
}
</script>

<style>

</style>