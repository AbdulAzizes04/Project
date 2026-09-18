const mongoose = require('mongoose');

const DatasetSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  filename: {
    type: String,
    required: true
  },
  filepath: {
    type: String,
    required: true
  },
  rowCount: {
    type: Number,
    default: 0
  },
  columnCount: {
    type: Number,
    default: 0
  },
  columns: {
    type: [mongoose.Schema.Types.Mixed],
    default: []
  },
  summary: {
    type: mongoose.Schema.Types.Mixed,
    default: {}
  },
  uploadedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  status: {
    type: String,
    enum: ['processing', 'active', 'failed'],
    default: 'processing'
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Dataset', DatasetSchema);
