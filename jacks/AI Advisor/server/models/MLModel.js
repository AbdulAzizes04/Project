const mongoose = require('mongoose');

const MLModelSchema = new mongoose.Schema({
  datasetId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Dataset',
    required: true
  },
  targetVariable: {
    type: String,
    required: true
  },
  taskType: {
    type: String,
    enum: ['classification', 'regression', 'forecast'],
    required: true
  },
  metrics: {
    type: mongoose.Schema.Types.Mixed,
    default: {}
  },
  featureImportance: {
    type: mongoose.Schema.Types.Mixed,
    default: {}
  },
  modelPath: {
    type: String,
    required: true
  },
  trainedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('MLModel', MLModelSchema);
