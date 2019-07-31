window.onload = () => {
  let csrftoken = (function getCookie(name) {
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
  })("csrftoken");

  removeProvider = function(button, provider) {
    let request = new XMLHttpRequest();
    let form = new FormData();

    let success = document.getElementById("delete-success");
    let fail = document.getElementById("delete-fail");

    form.append("provider", provider);

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
      "/api/provider/delete"
    )
    request.setRequestHeader("X-CSRFToken", csrftoken);
    request.send(form);
  }

  let providerSelector = document.getElementById("chosen-provider");
  let scopeGroup = document.getElementById("scope-group");
  let scopeBoxes = document.getElementById("chosen-scopes");
  let addButton = document.getElementById("add-button");
  let scopesToAdd = [];

  const greenButton = "btn btn-round btn-success tooltip-test";
  const purpleButton = "btn btn-round btn-primary tooltip-test";
  const redButton = "btn btn-round btn-danger tooltip-test";
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

  function selectorChange() {
    scopeGroup.style.display = "none";
    scopeBoxes.innerHTML = "";
    addButton.disabled = true;
    let provider = providerSelector.value;
    scopesToAdd = [];

    if (provider) {

      let request = new XMLHttpRequest();
      let form = new FormData();

      form.append("provider", provider);
      
      request.onreadystatechange = () => {

        if (request.readyState === 4 && request.status === 200) {
          let response = JSON.parse(request.responseText);

          response.forEach((scope, index) => {
            let formButton = scopeBoxes.appendChild(document.createElement("button"));
            formButton.innerHTML = "<i class=\"material-icons\">add</i>" + scope.simple_name;
            formButton.className = purpleButton;
            formButton.title = scope.description;
            formButton.onclick = () => {
              if (formButton.className === greenButton || formButton.className === redButton) {
                scopesToAdd = scopesToAdd.filter(scope => scope != scope.value);
                formButton.className = purpleButton;
                formButton.innerHTML = "<i class=\"material-icons\">add</i>" + scope.simple_name;
                formButton.onmouseover = null;
                formButton.onmouseleave = null;
              } else {
                scopesToAdd.push(scope.value);
                formButton.innerHTML = "<i class=\"material-icons\">check</i>" + scope.simple_name;
                formButton.className = greenButton;
                formButton.onmouseover = () => {
                  formButton.innerHTML = "<i class=\"material-icons\">remove</i>" + scope.simple_name;
                  formButton.className = redButton;
                }
                formButton.onmouseleave = () => {
                  formButton.innerHTML = "<i class=\"material-icons\">check</i>" + scope.simple_name;
                  formButton.className = greenButton;
                }
              }

              return false;
            };
          })

          scopeGroup.style.display = "";
          addButton.disabled = false;
        }
      }

      request.open(
        "POST",
        "/api/provider/scopes"
      )

      request.setRequestHeader("X-CSRFToken", csrftoken);
      request.send(form);
    }
  }
  providerSelector.onchange = selectorChange;
  selectorChange();

  addButton.onclick = () => {
    addButton.disabled = true;
    providerSelector.disabled = true;
    let provider = providerSelector.value;

    let buttons = scopeBoxes.getElementsByClassName("button");
    Array.prototype.forEach.call(buttons, button => button.disabled = true);
    let w = window.open("/oauth/" + provider + "?scopes=" + scopesToAdd.join("+"));
    setInterval(() => {
      if (w.closed) location.reload();
    }, 1000);
  }

  let timestamps = document.getElementsByClassName("timestamp");
  Array.prototype.forEach.call(timestamps, timestamp => {
    let unixTs = parseInt(timestamp.innerHTML) * 1000;
    let datetime = new Date(unixTs);
    
    let half = (datetime.getHours() % 12) ==  datetime.getHours() ? "AM" : "PM";
    let hour = datetime.getHours() % 12;
    hour = hour ? hour : 12;

    let string = hour + ":" + datetime.getMinutes() + half + " " + datetime.getDate() + " " + months[datetime.getMonth()] + " " + datetime.getFullYear();
    timestamp.innerHTML = string;
    timestamp.style.display = "";
  })
}