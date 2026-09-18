require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();

// Standard Middlewares
app.use(cors());
app.use(express.json());

// Set up public/static directories if needed
const reportsDir = path.resolve(path.join(__dirname, '..', 'reports'));
if (!fs.existsSync(reportsDir)) {
  fs.mkdirSync(reportsDir, { recursive: true });
}
app.use('/reports', express.static(reportsDir));

// Database connection
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/ai_advisor';
mongoose.connect(MONGODB_URI)
  .then(async () => {
    console.log('MongoDB database connected successfully!');
    try {
      const db = mongoose.connection.db;
      const count = await db.collection('users').countDocuments();
      if (count === 0) {
        console.log('MongoDB database is empty. Running initial sync from fallback db.json...');
        const runMigration = require('./migrate');
        await runMigration();
      }
    } catch (e) {
      console.warn('Auto-sync check notice:', e.message);
    }
  })
  .catch((err) => {
    console.warn('MongoDB connection failed. Starting Node server in fallback JSON database mode.');
    console.warn('Reason:', err.message);
  });

// API Routes
app.use('/api/auth', require('./routes/authRoutes'));
app.use('/api/datasets', require('./routes/datasetRoutes'));
app.use('/api/admin', require('./routes/adminRoutes'));

// Root path diagnostic route
app.get('/', (req, res) => {
  res.json({
    status: 'online',
    message: 'AI Business Advisor API Gateway is running',
    mode: mongoose.connection.readyState === 1 ? 'mongodb' : 'fallback-file-db'
  });
});

// Global Error Handler
app.use((err, req, res, next) => {
  console.error('Unhandled server error:', err.stack || err.message);
  res.status(err.status || 500).json({
    message: err.message || 'Internal Server Error'
  });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Express server running on port ${PORT}`);
});
