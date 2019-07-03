const policyArea = document.getElementById("policyTextarea");

policyArea.addEventListener("input", function(inputUpdate) {
  updateVisualization(inputUpdate.srcElement.value)
});

const request = new XMLHttpRequest();
request.onreadystatechange = processResponse;

updateVisualization(policyArea.value);

function updateVisualization(value) {
  var formData = new FormData();
  formData.append("policy", value);

  request.open(
    "POST",
    "/api/parse_policy"
  );

  request.send(formData);
}

function processResponse() {
  if (request.readyState === 4 && request.status === 200) {
    //console.log(request.responseText);
    var request_json = JSON.parse(request.responseText);
    frame = document.getElementById("graph-frame")
    
    if (request_json["status"] == 'ok') {
      frame.innerHTML = request_json["parsed_policy"];
      console.log(frame.innerHTML)
      frame.removeAttribute("data-processed");
      mermaid.init(undefined, frame);
    } else {
      console.log(request_json["traceback"])
    }

  }
}
