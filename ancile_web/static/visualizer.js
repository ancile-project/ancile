const policyArea = document.getElementById("policyTextarea");

policyArea.addEventListener("input", function(inputUpdate) {
  updateVisualization(inputUpdate.srcElement.value)
});

const request = new XMLHttpRequest();
const idRegex = /(?:^|\n)([A-Z]*)([0-9]+)/g;
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
      frame.innerHTML = parsePolicy(request_json["parsed_policy"])["code"];
      //console.log(frame.innerHTML)
      frame.removeAttribute("data-processed");
      mermaid.init(undefined, frame);
    } else {
      //console.log(request_json["traceback"])
    }

  }
}

function objectToString(object) {
  var objectString = ""
  for (key in object) {
    objectString += key + "=" + value + ", "
  }

  return objectString.slice(0, -2);
}

function findMaxId(children) {
  var max = 0;
  for (index in children) {
    if (children[index]["id"] > max) {
      max = children[index]["id"] > max;
    }
  }
  return max;
}

function parsePolicy(policy, parents, code, currentId, star) {
  console.log(policy);
  if (code == undefined) {
    code = "graph TD\n";
  }

  if (parents == undefined) {
    parents = [];
  }

  if (currentId == undefined) {
    currentId = {
      "branch": "",
      "id": 0
    };
  }

  if (star == undefined) {
    star = false;
  }
  
  if (policy[0] == "exec") {
    var elementName = currentId["branch"] + currentId["id"];
    code += elementName + "[" + policy[1] + "]\n";
    // console.log(parents);
    for (i in parents) {
      code += (parents[i]["branch"] + parents[i]["id"]) + " --> " + elementName + "\n";
    }
    if (star == true) {
      for (i in parents) {
        code += elementName + " --> "  + "\n" + (parents[i]["branch"] + parents[i]["id"]);
      }
    }

    return {
      "children": [currentId],
      "code": code
    };
  }

  else if (policy[0] == "concat") {

    var result = parsePolicy(policy[1], parents, code, currentId);
    
    result = parsePolicy(policy[2], result["children"], result["code"], {
      "branch": currentId["branch"],
      "id": findMaxId(result["children"]) + 1
    });

    return result;
  }

  else if (policy[0] == "union") {
    var result = parsePolicy(policy[1], parents, code, {
      "branch": currentId["branch"] + "A",
      "id": currentId["id"]
    });

    var secondResult = parsePolicy(policy[2], parents, result["code"], {
      "branch": currentId["branch"] + "B",
      "id": currentId["id"]
    });

    return {
      "children": result["children"].concat(secondResult["children"]),
      "code": secondResult["code"]
    };
  }
  
  else if (policy[0] == "star") {

    var result = parsePolicy(policy[1], parents, code, currentId, true);

    matches = [...result["code"].matchAll(idRegex)];
    
  }

  else {
    return {
      "children": [],
      "code": code
    };
  }
}
