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

  let bytes = file[0].size;
  let time = bytes/(1500 * 6.5);
  let interval = (time/100) * 1000;
  console.log(interval)
  let percent = 0;
  let progress = window.setInterval(function () {
    console.log(percent)
    if (percent <= 100) {
      document.getElementById('progress-bar').style.width = percent + '%';
    }
    percent++;
  },interval)

  x.onreadystatechange = function () {
    if(x.readyState == 4) {
      
      document.getElementById('drop-zone').classList.remove('dropped-file')
      document.getElementById('upload-bar').classList.remove('dropped-file')

      if(x.status == 200) {
        // success
        document.getElementById('progress-bar').style.width = '100%';
        window.clearInterval(progress);
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