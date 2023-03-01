const express = require("express");
const upload = require("express-fileupload");
const path = require("path");

const app = express();

app.use(express.json());
app.use(express.urlencoded( { extended: false } )); // this is to handle URL encoded data
app.use(upload());

app.use(express.static(path.join(__dirname, "public")));

app.get('/files', function(req, res) {
  var fs = require('fs');
  var files = fs.readdirSync('./public/snakedata');
  
  console.log('Get request: ' + files);
  
  res.send(files);
});

var fileIdx = 1;
app.post("/upload", function(request, response) {

  var images = new Array();
  if(request.files) {
    
    var file = request.files['file'];
    
    var file_name = "/" + file.name;
    
    file.mv("./public/snakedata" + file_name, function (err) {
        if(err) {
            console.log(err);
        }
    });
    console.log("file " + fileIdx + " uploaded")
    fileIdx++;
  }
  // give the server a second to write the files
  setTimeout(function(){response.json(images);}, 1000);
});

// set port from environment variable, or 8080
const PORT = process.env.PORT || 8080;

app.listen(PORT, () => console.log(`listening on port ${PORT}`));