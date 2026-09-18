const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const User = require('../models/User');
const Dataset = require('../models/Dataset');
const MLModel = require('../models/MLModel');
const fallbackDb = require('../data/fallback_db');
const fs = require('fs');
const path = require('path');

// Middleware to verify Admin role
const adminOnly = (req, res, next) => {
  if (req.user && req.user.role === 'admin') {
    next();
  } else {
    res.status(403).json({ message: 'Access denied: Admin role required' });
  }
};

const isMongoConnected = () => {
  const mongoose = require('mongoose');
  return mongoose.connection.readyState === 1;
};

// GET /api/admin/users
router.get('/users', auth, adminOnly, async (req, res) => {
  try {
    let users;
    if (isMongoConnected()) {
      users = await User.find().select('-password').sort({ createdAt: -1 });
    } else {
      users = await fallbackDb.users.find({});
      // Hide passwords
      users = users.map(u => {
        const { password, ...safeUser } = u;
        return safeUser;
      });
    }
    res.json(users);
  } catch (err) {
    console.error('Admin users fetch error:', err.message);
    res.status(500).json({ message: 'Server error' });
  }
});

// GET /api/admin/stats
router.get('/stats', auth, adminOnly, async (req, res) => {
  try {
    let userCount = 0;
    let datasetCount = 0;
    let modelCount = 0;
    let totalRows = 0;

    if (isMongoConnected()) {
      userCount = await User.countDocuments();
      datasetCount = await Dataset.countDocuments();
      modelCount = await MLModel.countDocuments();
      
      const datasets = await Dataset.find({}, 'rowCount');
      totalRows = datasets.reduce((sum, d) => sum + (d.rowCount || 0), 0);
    } else {
      const users = await fallbackDb.users.find({});
      const datasets = await fallbackDb.datasets.find({});
      const models = await fallbackDb.models.find({});
      
      userCount = users.length;
      datasetCount = datasets.length;
      modelCount = models.length;
      totalRows = datasets.reduce((sum, d) => sum + (d.rowCount || 0), 0);
    }

    // Calculate physical storage size of datasets/ directory
    const datasetsDir = path.resolve(path.join(__dirname, '..', '..', 'datasets'));
    let storageBytes = 0;
    if (fs.existsSync(datasetsDir)) {
      const files = fs.readdirSync(datasetsDir);
      files.forEach(f => {
        const stats = fs.statSync(path.join(datasetsDir, f));
        if (stats.isFile()) {
          storageBytes += stats.size;
        }
      });
    }

    res.json({
      userCount,
      datasetCount,
      modelCount,
      totalRows,
      storageUsedMB: Number((storageBytes / (1024 * 1024)).toFixed(2))
    });
  } catch (err) {
    console.error('Admin stats fetch error:', err.message);
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router;
