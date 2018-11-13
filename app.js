const express = require("express");
const app = express();

const bodyParser = require("body-parser");
const findClosestMsjdRoutes = require("./api/routes/findClosestMsjdRouter");

// middle wheres
//app.use(bodyParser.urlencoded({ extended: false }));
//app.use(bodyParser.json());

app.use("/findClosestMsjd", findClosestMsjdRoutes);

// handel all errors
app.use((error, req, res, next) => {
  res.status(error.status || 500);
  res.json({
    error: {
      message: error.message
    }
  });
});

module.exports = app;
