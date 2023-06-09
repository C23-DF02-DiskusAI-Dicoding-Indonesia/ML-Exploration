// Importing required modules
const express = require('express');
const path = require('path');

// Creating an instance of Express
const app = express();

// Set up static files
app.use(express.static('public'));

// Define routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/chatbot-gpt', (req, res) => {
  res.sendFile(path.join(__dirname, 'chatbot-gpt.html'));
});

app.get('/chatbot', (req, res) => {
  res.sendFile(path.join(__dirname, 'chatbot.html'));
});

app.get('/searchbar', (req, res) => {
  res.sendFile(path.join(__dirname, 'searchbar.html'));
});

app.get('/integrated', (req, res) => {
  res.sendFile(path.join(__dirname, 'integrated.html'));
});

// Start the server
const port = 4000;
app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
