const mongoose = require('mongoose');

const ChatHistorySchema = new mongoose.Schema({
  datasetId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Dataset',
    required: true
  },
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  messages: [{
    role: {
      type: String,
      enum: ['user', 'assistant'],
      required: true
    },
    content: {
      type: String,
      required: true
    },
    timestamp: {
      type: Date,
      default: Date.now
    }
  }],
  updatedAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('ChatHistory', ChatHistorySchema);
