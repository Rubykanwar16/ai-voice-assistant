const express = require("express");
const cors = require("cors");   // ✅ add this

const app = express();

app.use(cors());  // ✅ VERY IMPORTANT

app.get("/greet", (req, res) => {
  res.json({ message: "Hello Ruby 👋" });
});

app.listen(5000, () => {
  console.log("Server running on port 5000");
});