const request = require("request");
const fs = require("fs");

const imageName = "2024-05-09_09-17-10_original.png";
const imagePath = `./newData/${imageName}`;

const data = fs.readFileSync(imagePath);
const url = "http://localhost:8080/prediction/json";
let start = new Date();

request.post(url, onResponse).form().append("file", data, {
  filename: "myfile.txt",
  contentType: "text/plain",
});

function onResponse(error, response, body) {
  if (!error && response.statusCode == 200) {
    console.log(`${imagePath}\n${body}`);
    console.error(Date.now() - start, "ms");
  } else {
    console.error(error);
  }
}
