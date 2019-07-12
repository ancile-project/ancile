window.onload = () => {
  const request = new XMLHttpRequest();
  request.onreadystatechange = processResponse;

  const policyArea = document.getElementById("policyTextarea");
  const policyFrame = document.getElementById("graph-frame");

  updateVisualization();

  policyArea.addEventListener("input", () => {
    updateVisualization()
  });

  function decodeHtml(html) {
    var txt = document.createElement("textarea");
    txt.innerHTML = html;
    return txt.value;
  }

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

  function clearFrame(theFrame) {
    theFrame.removeAttribute("data-processed");
    theFrame.innerHTML = "";
  }

  function changeSvg(svg) {
    policyFrame.innerHTML = svg;
  }

  function processResponse() {
    if (request.readyState === 4 && request.status === 200) {

      var request_json = JSON.parse(request.responseText);
      frame = document.getElementById("graph-frame")
      
      if (request_json["status"] == 'ok') {
        var content = request_json["parsed_policy"];
        clearFrame(policyFrame);
        mermaid.render('id1', content, changeSvg)
      }
    }
  }
}