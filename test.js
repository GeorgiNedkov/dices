const request = require("request");
const fs = require("fs");

const { images } = require("./images.js");
// const images = ["2024-06-09_07-04-58_original.png"];
const url = "http://localhost:8080/prediction/json";
// const url =
//   "https://dice-server-x86-187387799008.europe-west9.run.app/prediction/json";
async function nextTest() {
  if (images.length == 0) {
    console.error("------------");
    return;
  }

  const image = images.pop();
  const data = await fs.promises.readFile(`./newData/${image}`);
  const start = Date.now();

  function onResponse(error, response, body) {
    if (!error && response.statusCode == 200) {
      console.log(`newData/${image}\n${body}`);
      console.error(
        `${images.length} images left, response time: ${Date.now() - start} ms`
      );

      void nextTest();
    }
  }

  request.post(url, onResponse).form().append("file", data, {
    filename: "myfile.txt",
    contentType: "text/plain",
  });
}

treads = 1;
for (let i = 0; i < treads; i++) {
  void nextTest();
}
