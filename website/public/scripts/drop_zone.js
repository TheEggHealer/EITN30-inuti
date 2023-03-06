function stopDefault(event) {
  event.stopPropagation();
  event.preventDefault();
}

function handleFile(event) {
  document.getElementById('drop-zone').classList.add('dropped-file')
  document.getElementById('upload-bar').classList.add('dropped-file')
  var file = event.target.files || event.dataTransfer.files;
  
  console.log(file)
  
  var fd = new FormData();
  fd.append('file', file[0], file[0].name);
  var x = new XMLHttpRequest();

  // let bytes = file[0].size;
  // let time = bytes/(1500 * 12.5);
  // let interval = (time/100) * 1000;
  // let percent = 0;
  // let progress = window.setInterval(function () {
  //   if (percent <= 100) {
  //     document.getElementById('progress-bar').style.width = percent + '%';
  //   }
  //   percent++;
  // },interval)
  if (x.upload) {
    x.upload.addEventListener('progress', function(event) {
      if (event.lengthComputable) {
        // Calculate the percentage of data transferred
        var percentComplete = parseInt(event.loaded / event.total * 100);
        console.log(percentComplete);
        // Update the progress bar
        document.getElementById('progress-bar').style.width = percentComplete + "%";
      }
    });
  }

  x.onreadystatechange = function () {
    if(x.readyState == 4) {
      
      document.getElementById('drop-zone').classList.remove('dropped-file')
      document.getElementById('upload-bar').classList.remove('dropped-file')

      if(x.status == 200) {
        // success
        // document.getElementById('progress-bar').style.width = '100%';
        // window.clearInterval(progress);
      }
      else {
        // failed - TODO: Add code to handle server errors
      }
    }
  };

  x.open("post", '/upload', true);
  x.send(fd);
  
  console.log('File uploaded')
}

function hoverFile(event) {
  event.preventDefault() 
  document.getElementById('drop-zone').classList.add('hover-file')
}

function unHoverFile(event) {
  event.preventDefault() 
  document.getElementById('drop-zone').classList.remove('hover-file')
}