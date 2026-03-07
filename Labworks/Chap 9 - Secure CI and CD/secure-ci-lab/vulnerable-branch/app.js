const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
  const name = req.query.name || 'World';
  res.send(`Hello ${name}!`);
});

// Vulnerable endpoint - triggers Semgrep SAST
app.get('/exec', (req, res) => {
  const result = eval(req.query.code);
  res.send(`Result: ${result}`);
});

app.listen(port, () => {
  console.log(`App listening at http://localhost:${port}`);
});
