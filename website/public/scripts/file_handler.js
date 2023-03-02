let currentFiles = [];
let deletedFiles = [];

let process = window.setInterval(updateFiles, 1000);

function updateFiles () {
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

        // Remove file from deleted_files if it is already deleted
        for(let i in deletedFiles) {
          idx = files.indexOf(deletedFiles[i]);
          if(idx == -1) {
            deletedFiles.splice(i, 1);
          }
        }
        
        // Remove file from list if it is currently getting deleted
        for(let i in files) {
          idx = deletedFiles.indexOf(files[i]);
          if(idx > -1)
            files.splice(i,1);
        }

        if(JSON.stringify(currentFiles) !== JSON.stringify(files)) {
          fileContainer.innerHTML = '';
  
          for(let i in files) {
            const clone = template.content.cloneNode(true);
            const name = clone.querySelectorAll("p");
            name[0].innerHTML = files[i];

            const link = clone.querySelectorAll("a");
            link[0].href = "/download?filename=" + files[i];


            //link[1].href = "/delete?filename=" + files[i];

            // const close = clone.querySelectorAll("#file-close-button")
            // close[0].href = "/dpwdpok"
  

            
            clone.querySelectorAll('.file-close')[0].addEventListener('click', event => {
              let closeReq = new XMLHttpRequest();
              deletedFiles.push(files[i]);
              updateFiles();
              closeReq.open('post', '/delete?filename=' + files[i], true);
              closeReq.send();
            });

            fileContainer.appendChild(clone);
          }

          currentFiles = files;
        }
      }
    }
  }
}

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