//cqol541r01qk9583a7tgcqol541r01qk9583a7u0
// backend/server.js

// backend/server.js

const express = require('express');
const axios = require('axios');
const cors = require('cors');
const path = require('path');

const app = express();
const port = 5000;
const FINNHUB_API_KEY = 'cqol541r01qk9583a7tgcqol541r01qk9583a7u0'; // Replace with your actual Finnhub API key

app.use(cors());
app.use(express.json());

app.get('/api/quote', async (req, res) => {
  try {
    const ticker = req.query.ticker;
    console.log(`Fetching quote for: ${ticker}`);
    const url = `https://finnhub.io/api/v1/quote?symbol=${ticker}&token=${FINNHUB_API_KEY}`;
    console.log(`Request URL: ${url}`);
    const response = await axios.get(url);
    console.log('Quote response:', response.data);
    res.json(response.data);
  } catch (error) {
    console.error('Error fetching quote:', error);
    if (error.response) {
      console.error('Error response data:', error.response.data);
      console.error('Error response status:', error.response.status);
      console.error('Error response headers:', error.response.headers);
      res.status(error.response.status).json({ error: error.response.data });
    } else if (error.request) {
      console.error('Error request:', error.request);
      res.status(500).json({ error: 'No response received from Finnhub' });
    } else {
      console.error('Error message:', error.message);
      res.status(500).json({ error: error.message });
    }
  }
});

app.get('/api/historical', async (req, res) => {
  try {
    const ticker = req.query.ticker;
    const resolution = req.query.interval;
    const from = req.query.period1;
    const to = req.query.period2;
    console.log(`Fetching historical data for: ${ticker} from ${from} to ${to} with resolution ${resolution}`);
    const url = `https://finnhub.io/api/v1/stock/candle?symbol=${ticker}&resolution=${resolution}&from=${from}&to=${to}&token=${FINNHUB_API_KEY}`;
    console.log(`Request URL: ${url}`);
    const response = await axios.get(url);
    console.log('Historical data response:', response.data);
    res.json(response.data);
  } catch (error) {
    console.error('Error fetching historical data:', error);
    if (error.response) {
      console.error('Error response data:', error.response.data);
      console.error('Error response status:', error.response.status);
      console.error('Error response headers:', error.response.headers);
      res.status(error.response.status).json({ error: error.response.data });
    } else if (error.request) {
      console.error('Error request:', error.request);
      res.status(500).json({ error: 'No response received from Finnhub' });
    } else {
      console.error('Error message:', error.message);
      res.status(500).json({ error: error.message });
    }
  }
});

// Serve the static files from the React app
app.use(express.static(path.join(__dirname, '../frontend/build')));

// Handles any requests that don't match the ones above
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/build/index.html'));
});

app.listen(port, () => {
  console.log(`Server is running at http://localhost:${port}`);
});