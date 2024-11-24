const fs = require("fs");
let fileData = fs.readFileSync("out-old.txt").toString();
let lines = fileData.split("\n").map((line) => line.trim());
let obj = {};

function haveSameElements(arr1, arr2) {
  if (arr1.length !== arr2.length) return false;

  return arr1.every((item) => arr2.includes(item));
}

for (let i = 0; i < lines.length; i += 3) {
  const name = lines[i];
  const data = lines[i + 1];
  try {
    obj[name] = JSON.parse(data);
  } catch (e) {
    console.error(i);
    throw e;
  }
}

fileData = fs.readFileSync("out.txt").toString();
lines = fileData.split("\n").map((line) => line.trim());
let totalTests = 0;
let failedTests = 0;

for (let i = 0; i < Math.floor(lines.length / 3) * 3; i += 3) {
  const name = lines[i];
  const data = JSON.parse(lines[i + 1]);
  totalTests += 1;
  if (obj[name].isValid == data.isValid && data.isValid == false) {
    continue;
  }

  if (haveSameElements(obj[name].value, data.value)) {
    continue;
  }

  failedTests += 1;
  console.log(name, "\n old: ", obj[name], "\n new: ", data);
}

console.error(`tastFailed: ${failedTests}, from total: ${totalTests}`);
