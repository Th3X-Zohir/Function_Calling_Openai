const express = require("express");
const bodyParser = require("body-parser");
const fs = require("fs");

const app = express();
const port = 3000;

// Use body-parser to parse JSON body
app.use(bodyParser.json());

// Function to read data from the JSON file
function readData() {
  try {
    const data = fs.readFileSync("data.json", "utf8");
    return JSON.parse(data);
  } catch (err) {
    console.error("Error reading from data.json:", err);
    return {}; // Return empty object if there's an error
  }
}

// Function to write data to the JSON file
function writeData(data) {
  try {
    fs.writeFileSync("data.json", JSON.stringify(data, null, 2), "utf8");
  } catch (err) {
    console.error("Error writing to data.json:", err);
  }
}

// POST endpoint to store data
app.post("/store", (req, res) => {
  const { key, value } = req.body;
  console.log(
    `Received POST request to store data: key = ${key}, value = ${value}`
  );

  let storage = readData();
  const id = Date.now(); // Unique ID based on the current timestamp
  storage[key] = { id, value };
  writeData(storage);

  console.log(`Data stored for key: ${key} with id: ${id}`);
  res.send(`Data stored for key: ${key} with id: ${id}`);
});

// GET endpoint to retrieve data
app.get("/retrieve/:key", (req, res) => {
  const key = req.params.key;
  console.log(`Received GET request to retrieve data for key: ${key}`);

  const storage = readData();
  const data = storage[key] || "No data for this key";

  console.log(`Retrieved data for key: ${key}:`, data);
  res.send(`Retrieved data: ${JSON.stringify(data)}`);
});

// PUT endpoint to update data
app.put("/update", (req, res) => {
  const { key, value } = req.body;
  console.log(
    `Received PUT request to update data: key = ${key}, value = ${value}`
  );

  let storage = readData();
  if (key in storage) {
    storage[key].value = value; // Update only the value, keep the same id
    writeData(storage);
    console.log(`Data updated for key: ${key}`);
    res.send(`Data updated for key: ${key}`);
  } else {
    res.send(`Key: ${key} not found`);
  }
});

// DELETE endpoint to delete data
app.delete("/delete/:key", (req, res) => {
  const key = req.params.key;
  console.log(`Received DELETE request to delete data for key: ${key}`);

  let storage = readData();
  if (key in storage) {
    delete storage[key];
    writeData(storage);
    console.log(`Data deleted for key: ${key}`);
    res.send(`Data deleted for key: ${key}`);
  } else {
    res.send(`Key: ${key} not found`);
  }
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
