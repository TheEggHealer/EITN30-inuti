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
        files.sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()));

        if(JSON.stringify(current_files) !== JSON.stringify(files)) {
          fileContainer.innerHTML = '';
  
          for(let i in files) {
            const clone = template.content.cloneNode(true);
            const name = clone.querySelectorAll("p");
            name[0].innerHTML = files[i];
            
            clone.querySelectorAll('.file')[0].addEventListener('click', event => {
              downloadFile(files[i]);
            });

            fileContainer.appendChild(clone);
          }

          current_files = files;
        }
      }
    }
  }
}, 1000);

function downloadFile(fileName) {
  console.log(fileName);
  
  window.open("/download?filename=" + fileName);

  // let x = new XMLHttpRequest();
  
  // x.open('get', '/download', true);
  // x.setRequestHeader('Content-Type', 'application/json;charset=UTF-8')
  // x.send();

  // x.onreadystatechange = function () {
  //   if(x.readyState == 4) {
  //     if(x.status == 200) {
  //       console.log('Downloaded');
  //     }
  //   }
  // }
}