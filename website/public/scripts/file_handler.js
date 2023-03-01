let current_files = [];

let process = window.setInterval(function () {
  let x = new XMLHttpRequest();
  x.open('get', '/files', true);
  x.send();
  x.onreadystatechange = function () {
    if(x.readyState == 4) {
      if(x.status == 200) {
        const files = JSON.parse(x.response);
        const fileContainer = document.getElementById('files-container');
        const template = document.getElementById('file-template')

        if(JSON.stringify(current_files) !== JSON.stringify(files)) {
          fileContainer.innerHTML = '';
  
          for(let i in files) {
            const clone = template.content.cloneNode(true);
            const name = clone.querySelectorAll("p");
            name[0].innerHTML = files[i]
    
            fileContainer.appendChild(clone);
          }

          current_files = files;
        }

      }
      

    }
  }


}, 1000);