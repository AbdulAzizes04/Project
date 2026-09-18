const express = require('express');
const router = express.Router();
const datasetController = require('../controllers/datasetController');
const auth = require('../middleware/auth');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

// Configure Multer storage to save datasets to the shared root datasets folder
const uploadDir = path.resolve(path.join(__dirname, '..', '..', 'datasets'));
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, uploadDir);
  },
  filename: function (req, file, cb) {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1e9);
    cb(null, 'dataset-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({
  storage: storage,
  fileFilter: (req, file, cb) => {
    const ext = path.extname(file.originalname).toLowerCase();
    if (ext === '.csv' || ext === '.xlsx' || ext === '.xls') {
      return cb(null, true);
    }
    cb(new Error('Only CSV or Excel files are allowed!'));
  }
});

// Upload and Process dataset
router.post('/upload', auth, upload.single('file'), datasetController.uploadDataset);

// Get all datasets for current user
router.get('/', auth, datasetController.getDatasets);

// Get specific dataset summary details
router.get('/:id', auth, datasetController.getDatasetById);

// Delete dataset
router.delete('/:id', auth, datasetController.deleteDataset);

// Rename dataset
router.patch('/:id', auth, datasetController.renameDataset);

// AI Chat with Dataset
router.post('/:id/chat', auth, datasetController.chatWithDataset);
router.get('/:id/chat', auth, datasetController.getChatHistory);

// Train ML Model
router.post('/:id/train', auth, datasetController.trainModel);
router.get('/:id/models', auth, datasetController.getModels);
router.post('/:id/predict', auth, datasetController.predict);

// Download PDF Report
router.get('/:id/report', auth, datasetController.generateReport);

module.exports = router;
