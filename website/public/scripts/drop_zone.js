function stopDefault(event) {
  event.stopPropagation();
  event.preventDefault();
}

function handleFile(event) {
  document.getElementById('drop-zone').classList.add('dropped-file')
  var file = event.target.files || event.dataTransfer.files;
  
  console.log(file)
  
  var fd = new FormData();
  fd.append('file', file[0], file[0].name);
  var x = new XMLHttpRequest();

  if(x.upload) {
    x.upload.addEventListener("progress", function(event){
      var percentage = parseInt(event.loaded / event.total * 100);
      // progress.innerText = progress.style.width = percentage + "%";
      document.getElementsByClassName('progress-bar').style.width = percentage + '%';
    });
  }
  x.onreadystatechange = function () {
    if(x.readyState == 4) {
      
      unHoverFile(event); // this will reset the text and styling of the drop zone
      if(x.status == 200) {
        // success
      }
      else {
        // failed - TODO: Add code to handle server errors
      }
    }
  };

  x.open("post", '/upload', true);
  x.send(fd);
  
  console.log('File uploaded')
  document.getElementById('drop-zone').classList.remove('dropped-file')
}

function hoverFile(event) {
  event.preventDefault() 
  document.getElementById('drop-zone').classList.add('hover-file')
}

function unHoverFile(event) {
  event.preventDefault() 
  document.getElementById('drop-zone').classList.remove('hover-file')
}