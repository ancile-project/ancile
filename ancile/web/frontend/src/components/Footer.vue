<template>
  <div id="footer">
    <vs-divider></vs-divider>
    <p>
      made with <vs-icon size="1em" color="danger" icon-pack="fas" icon="fa-heart"></vs-icon> @ <a target="_blank" href="http://smalldata.io">small data lab</a>
    </p>
  </div>
</template>

<script>
export default {
  name: "Footer",
}
</script>

<style scoped>
#footer {
  position: static;
  bottom: 0px;
  height: 60px;
  width: 100%;
  text-align: right;
}

p {
  padding-right: 10px;
  font-size: small;
}
</style>