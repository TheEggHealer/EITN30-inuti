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

  res.send(files);
});

app.get('/download', function (req, res) {
  let fileName = req.query['filename'];

  res.download('./public/snakedata/' + fileName, fileName);
});

app.post("/delete", function (req, res) {
  let fileName = req.query['filename'];

  var fs = require('fs');
  fs.unlinkSync('./public/snakedata/' + fileName);
  console.log(fileName + ' deleted')
});

app.post("/upload", function(request, response) {

  var images = new Array();
  if(request.files) {
    
    var file = request.files['file'];
    
    var fileName = file.name;
    
    file.mv("./public/snakedata/" + fileName, function (err) {
        if(err) {
            console.log(err);
        }
    });
    console.log(fileName + ' uploaded')
  }
  // give the server a second to write the files
  setTimeout(function(){response.json(images);}, 1000);
});

// set port from environment variable, or 8080
const PORT = process.env.PORT || 8080;

app.listen(PORT, () => console.log(`listening on port ${PORT}`));