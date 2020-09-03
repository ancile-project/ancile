<template>
  <div v-html="html" class="mermaid">
  </div>
</template>

<script>
import mermaid from 'mermaid';
mermaidAPI.initialize({    
    securityLevel: 'antiscript' 
});

export default {
  name: "PolicyVisual",
  props: {
    policy: {
      type: String,
      default: ""
    }
  },
  data() {
    return {
      html: ""
    }
  },
  watch: {
    policy(newPolicy) {
      const endpoint = "/api/parse_policy";
      const data = { policy: newPolicy };
      var graph = "graph TD\n A[Error]";
      this.$store.dispatch("post", { endpoint, data })
        .then(resp => {
          if (resp.data.graph) graph = resp.data.graph;
        })
        .catch(() => {})
        .finally(() => {
          mermaid.render("policy-graph", graph, html => this.html = html);
        })

    }
  }
}
</script>

<style>
g > .path {
 -webkit-animation: none !important;
 animation: none !important;
}

.mermaid {
  text-align: center;
}
</style>
