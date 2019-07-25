// The whole program body is in one function that will be executed
// when the page fully loads (to avoid null HTML fields).
window.onload = () => {

  // HTTP request object calls the processResponse()
  // function whenever there's a state change
  const request = new XMLHttpRequest();
  request.onreadystatechange = processResponse;

  // the policyArea is where the policy text is stored
  // the policyFrame is the div element where the flowchart is placed
  const policyArea = document.getElementById("policyTextarea");
  const policyFrame = document.getElementById("graph-frame");

  // run updateVisualization for the first time
  updateVisualization();

  // add a lister that calls updateVisualizer()  whenever
  // user input in that field is detected
  policyArea.addEventListener("input", () => {
    updateVisualization()
  });

  /*
    Decodes HTML text. This is a problem with ">" and "<" operators. 
    It works by creating a textarea HTML element and putting the text there 
    (since textarea doesn't encode the text by default)

    @param {String} HTML-encoded string
    @return {String} decoded string
  */
  function decodeHtml(html) {
    var txt = document.createElement("textarea");
    txt.innerHTML = html;
    return txt.value;
  }

  /*
    Fetches the policy from policyArea and sends a request to the ancile
    parser API using the request XMLHTTPRequest object.
  */
  function updateVisualization() {
    var policyText = policyArea.value || policyArea.innerHTML;
    policyText = decodeHtml(policyText);
    
    var formData = new FormData();
    formData.append("policy", policyText);

    request.open(
      "POST",
      "/api/parse_policy"
    );

    request.send(formData);
  }

  /*
    Clears the policyFrame so mermaidJS can re-rerender the chart.

    @param {Element} The frame's DOM element object
  */
  function clearFrame(theFrame) {
    theFrame.removeAttribute("data-processed");
    theFrame.innerHTML = "";
  }

  /*
    Places the svg inside policyFrame

    @param {String} svg image
  */
  function changeSvg(svg) {
    policyFrame.innerHTML = svg;
  }

  /*
    Processes the response when the state of the request object
    changes.
  */
  function processResponse() {
    if (request.readyState === 4 && request.status === 200) {

      var request_json = JSON.parse(request.responseText);
      
      if (request_json.status == 'ok') {

        var content = request_json.parsed_policy;
        clearFrame(policyFrame);
        mermaid.render('id1', content, changeSvg);

      }
    }
  }
}