const request = require("request");
const fs = require("fs");
const data = fs.readFileSync("./data/2024-05-09_09-17-10_original.png");
let date = new Date();

request
  .post("http://localhost:31415/prediction/json", onResponse)
  .form()
  .append("file", data, {
    filename: "myfile.txt",
    contentType: "text/plain",
  });

function onResponse(error, response, body) {
  if (!error && response.statusCode == 200) {
    console.log(body);
    console.error(new Date() - date);
    date = new Date();
  }
}
