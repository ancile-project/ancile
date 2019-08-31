<template>
  <div id="header">
    <vs-row vs-justify="center">
      <vs-col type="flex" vs-justify="center" vs-align="center" vs-w="1">
          <div id="title">
            <h2>
              <router-link to="/"><span id="title-text">Ancile</span></router-link>
            </h2>
          </div>
      </vs-col>
    </vs-row>
  </div>
</template>


<script>
export default {
  name: "Header",
}
</script>

<style>
#header {
  display: flex;
  align-items: center;
  background-color: rgb(var(--vs-primary), 1);
  height: 51px;
  width: 100%;
}

#title-text {
  color: white;
}
</style>