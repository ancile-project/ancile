const policyArea = document.getElementById("policyTextarea");

policyArea.addEventListener("input", updateVisualization);
const request = new XMLHttpRequest();
request.onreadystatechange = processResponse;

function updateVisualization(inputUpdate) {
  var currentValue = inputUpdate.srcElement.value;
  var formData = new FormData();
  formData.append("policy", currentValue);

  request.open(
    "POST",
    "/api/parse_policy"
  );

  request.send(formData);
}

function processResponse() {
  if (request.readyState === 4 && request.status === 200) {
    console.log(request.responseText);
    var request_json = JSON.parse(request.responseText);
    frame = document.getElementById("graph-frame")
    
    if (request_json["status"] == 'ok') {
      frame.innerHTML = policyToGraph(request_json["parsed_policy"]);
      console.log(frame.innerHTML)
    } else {
      frame.innerHTML = "graph TD\n0[Error]";
    }
    frame.removeAttribute("data-processed");
    mermaid.init(undefined, frame);
  }
}

function objectToString(object) {
  var objectString = ""
  for (key in object) {
    objectString += key + "=" + value + ", "
  }

  return objectString.slice(0, -2);
}

function policyToGraph(policy, parentNumber, mermaidCode, nextNumber, branch, parentBranch) {
  if (mermaidCode === undefined) mermaidCode = "graph TD\n";
  if (branch == undefined) branch = "";
  if (parentBranch == undefined) parentBranch = branch;

  if (nextNumber == undefined) {
    if (parentNumber == undefined) {
      nextNumber = 0;
    } else {
      nextNumber = parentNumber + 1;
    }
  }



  console.log(nextNumber);

  if (policy[0] == "exec") {

    if (parentNumber != undefined) {
      mermaidCode += parentBranch + parentNumber + " --> " + branch + nextNumber + "[" + policy[1];
    } else {
      mermaidCode += "0[" + policy[1];
    }

    if (Object.keys(policy[2]) != 0) {
      mermaidCode += "(" + objectToString(policy[2]) + ")";
    }

    mermaidCode += "]\n";

  } else if (policy[0] == "concat") {
    mermaidCode = policyToGraph(policy[1], parentNumber, mermaidCode, undefined, branch, parentBranch);
    mermaidCode = policyToGraph(policy[2], nextNumber, mermaidCode, undefined, branch);
  } else if (policy[0] == "union") {
    branchA = branch + 'A';
    branchB = branch + "B";
    mermaidCode = policyToGraph(policy[1], parentNumber, mermaidCode, nextNumber, branchA, branch);
    mermaidCode = policyToGraph(policy[2], parentNumber, mermaidCode, nextNumber, branchB, branch);

  }

  return mermaidCode;
}