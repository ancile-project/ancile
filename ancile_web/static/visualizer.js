const request = new XMLHttpRequest();
request.onreadystatechange = processResponse;

window.onload = () => { 
  policyArea = document.getElementById("policyTextarea");
  policyFrame = document.getElementById("graph-frame");

  if (policyArea.value === undefined) {
    updateVisualization(policyArea.innerHTML);
  } else {
    updateVisualization(policyArea.value);
  }

  policyArea.addEventListener("input", function(inputUpdate) {
    updateVisualization(inputUpdate.srcElement.value)
  });

} ;

function updateVisualization(value) {
  var formData = new FormData();
  formData.append("policy", value);

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
    //console.log(request.responseText);
    var request_json = JSON.parse(request.responseText);
    frame = document.getElementById("graph-frame")
    
    if (request_json["status"] == 'ok') {
      var content = request_json["parsed_policy"];
      clearFrame(policyFrame);
      mermaid.render('id1', content, changeSvg)
    } else {
      console.log(request_json["traceback"])
    }

  }
}
