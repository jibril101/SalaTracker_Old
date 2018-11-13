const express = require("express");
const router = express.Router();

const path = require("path");

router.get("/", (req, res, next) => {
  // get the path of the script
  scriptPath =
    path.dirname(__filename) + "/../../findTheClosestMsjdAndTime.py";
  scriptPath = path.resolve(scriptPath);

  // run the script
  const spawn = require("child_process").spawn;
  const pythonProcess = spawn("python", [
    scriptPath,
    req.query.lat,
    req.query.lon
  ]);

  
  //python prints
  pythonProcess.stdout.on("data", function(data) {
    res.end(data.toString());
  });

  //pythons errors
  pythonProcess.stderr.on("data", function(data) {
    console.error(data.toString());
  });
});

module.exports = router;
