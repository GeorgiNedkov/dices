const request = require("request");
const fs = require("fs");
const data = fs.readFileSync("./data/2024-05-09_09-17-10_original.png");
let date = new Date();

options = {
  url: "http://localhost:31415/prediction/image",
  encoding: null, // otherwise image is Gibberish
  json: false,
  method: "POST",
};

request(options, (error, response, body) => {
  fs.writeFileSync("out.png", body);
  console.error(new Date() - date);
  date = new Date();
})
  .form()
  .append("file", data, {
    filename: "myfile.txt",
    contentType: "text/plain",
  });
