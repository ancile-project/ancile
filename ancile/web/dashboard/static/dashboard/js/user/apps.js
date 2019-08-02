window.onload = () => {
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }

  removeApp = function(button, app) {
    let request = new XMLHttpRequest();
    let form = new FormData();

    let success = document.getElementById("delete-success");
    let fail = document.getElementById("delete-fail");

    form.append("app", app);

    request.onreadystatechange = () => {
      if (request.readyState === 4 && request.status === 200) {
        let response = JSON.parse(request.responseText);

        if (response.status === "ok") {
          let row = button.parentNode.parentNode;
          row.parentNode.removeChild(row);
          success.style.display = "";
          setTimeout(() => {
            success.style.display = "none";
          }, 3000)
        } else {
          fail.innerHTML = response.error;
          fail.style.display = "";
          setTimeout(() => {
            fail.style.display = "none";
          }, 3000)
        }
      }
    }

    request.open(
      "POST",
      "/api/app/delete"
    )
    request.setRequestHeader("X-CSRFToken", csrftoken);
    request.send(form);
  }

  var windows = []
  var addButton = document.getElementById("add-app-button");
  var csrftoken = getCookie('csrftoken');
  var appSelector = document.getElementById("chosen-app");
  var permissionSelector = document.getElementById("chosen-group");

  var permissionGroup = document.getElementById("permission-group");
  var permissionTable = document.getElementById("permission-table");
  
  var policyModalTitle = document.getElementById("policy-modal-title")
  var policyModalBody = document.getElementById("policy-modal-body");

  var blankOption = new Option("", "", true, true);
  var groupCard = document.getElementById("group-card");
  var groupTitle = document.getElementById("group-title");
  var groupDescription = document.getElementById("group-description");

  function reloadGroups() {
    var newValue = appSelector.value;
    permissionSelector.options.length = 0;
    permissionSelector.options.add(blankOption);

    if (newValue) {
      permissionGroup.style.display = "";
      permissionSelector.disabled = true;

      var request = new XMLHttpRequest();
      var form = new FormData();

      form.append("app", newValue);
      request.onreadystatechange = () => {
        if (request.status === 200 && request.readyState === 4) {
          var groups = JSON.parse(request.responseText);
          groups.forEach(group => {
            let option = new Option(group);
            permissionSelector.options.add(option);
          });
          permissionSelector.disabled = false;
        }
      }

      request.open(
        "POST",
        "/api/app/groups"
      )
      request.setRequestHeader("X-CSRFToken", csrftoken);
      request.send(form);
    } else {
      permissionGroup.style.display = 'none';
      groupCard.style.display = 'none';
      permissionTable.style.display = 'none';

    }
  }

  function startAuth(provider, scopes, callback) {
    return () => {
      let authUrl = "/oauth/" + provider + "?scopes=" + scopes.join("+");
      let authWindow = window.open(authUrl);
      windows.push(authWindow);
    }
  }

  function reloadTable(noHide) {
    var appName = appSelector.value;
    var groupName = permissionSelector.value;
    if (!noHide) {
      permissionTable.style.display = "none";
      groupCard.style.display = "none";
    } 

    if (groupName) {
      let request = new XMLHttpRequest();
      let form = new FormData();

      form.append("app", appName)
      form.append("group", groupName);

      request.onreadystatechange = () => {

        if (request.status === 200 && request.readyState === 4) {
          let allGood = true;
          let newTBody = permissionTable.getElementsByTagName("tbody")[0];
          newTBody.innerHTML = "";

          let response = JSON.parse(request.responseText);
          let providers = response.providers;
          groupTitle.innerHTML = groupName;
          groupDescription.innerHTML = response.description;

          providers.forEach(provider => {
            let newRow = newTBody.insertRow();

            let nameCell = newRow.insertCell(0);
            nameCell.appendChild(document.createTextNode(provider.display_name));

            let scopeCell = newRow.insertCell(1);
            let scopeList = scopeCell.appendChild(document.createElement("ul"));
            let scopes = []
            provider.scopes.forEach(scope => {
              let scopeListElement = scopeList.appendChild(document.createElement("li"));
              scopeListElement.appendChild(document.createTextNode(scope.simple_name));
              scopes.push(scope.value);
            })

            let statusCell = newRow.insertCell(2);
            let statusObject = statusCell.appendChild(document.createElement("i"));
            statusObject.className = "material-icons";
            statusObject.innerHTML = provider.status ? "check" : "close";
            allGood = provider.status && allGood;

            let authCell = newRow.insertCell(3);
            let authButton = authCell.appendChild(document.createElement("button"));
            if (provider.status) {
              authButton.disabled = true;
              authButton.innerHTML = "Authorized";
              authButton.className = "btn btn-success"
            } else {
              authButton.disabled = false;
              authButton.innerHTML = "Authorize";
              authButton.onclick = startAuth(provider.path_name, scopes);
              authButton.className = "btn btn-info"
            }
          });
          permissionTable.style.display = "";
          groupCard.style.display = "";
          addButton.disabled = !allGood;
        }

      }

      request.open(
        "POST",
        "/api/app/permissions"
      );
      request.setRequestHeader("X-CSRFToken", csrftoken);
      request.send(form);

    } else {
      permissionTable.style.display = "none";
    }
  }

  addButton.onclick = () => {
    var success = document.getElementById("add-success");
    var fail = document.getElementById("add-fail");
    fail.style.display = "none";
    addButton.disabled = true;

    let request = new XMLHttpRequest();
    let form = new FormData();
    form.append("app", appSelector.value);
    form.append("group", permissionSelector.value);

    request.onreadystatechange = () => {

      if (request.readyState === 4 && request.status === 200) {
        let response = JSON.parse(request.responseText);

        if (response.status == "ok") {
          success.style.display = "";
          location.reload();
        } else {
          fail.innerHTML = response.error;
          fail.style.display = "";
          addButton.disabled = false;
        }
      }
    }

    request.open(
      "POST",
      "/api/app/add"
    )
    request.setRequestHeader("X-CSRFToken", csrftoken);
    request.send(form);
  }

  appSelector.onchange = reloadGroups;
  permissionSelector.onchange = reloadTable;

  window.setInterval(function() {
    windows.forEach(win => {
      if (win.closed) {
        reloadTable(true);
      }
    })
    windows = windows.filter(win => !win.closed)
  }, 1000);

  reloadGroups();

  showPolicies = function(app) {
    let request = new XMLHttpRequest();
    let form = new FormData();

    form.append("app", app);

    request.onreadystatechange = () => {
      
      if (request.readyState === 4 && request.status === 200) {
        response = JSON.parse(request.responseText);
        policyModalTitle.innerHTML = app + " policies";
        policyModalBody.innerHTML = "";
        response.forEach(provider => {
          let card = policyModalBody.appendChild(document.createElement("div"));
          card.className = "card";
          card.style.textAlign = "center";
          card.innerHTML = `
          <div class="card-header">
          <h4 class="card-title">${provider.provider}</h4>
          </div>
          <div class="card-body">
            <div class="mermaid"></div>
          </div>
          `
          let frame = card.getElementsByClassName("mermaid")[0];
          mermaid.render(provider.provider.split(" ").join("-"), provider.policy, svg => frame.innerHTML = svg);
        });
      }

    }

    request.open("POST", "/api/app/policies")
    request.setRequestHeader("X-CSRFToken", csrftoken);
    request.send(form);
  }
}