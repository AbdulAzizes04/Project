const Dataset = require('../models/Dataset');
const MLModel = require('../models/MLModel');
const ChatHistory = require('../models/ChatHistory');
const fallbackDb = require('../data/fallback_db');
const LLMService = require('../services/llm');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const PDFDocument = require('pdfkit');

const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://localhost:8000';

// Helper to determine if we should use fallback DB
const isMongoConnected = () => {
  const mongoose = require('mongoose');
  return mongoose.connection.readyState === 1;
};

// 1. Upload & Process Dataset
exports.uploadDataset = async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ message: 'Please upload a CSV or Excel file' });
  }

  const filepath = path.resolve(req.file.path);
  const filename = req.file.filename;
  const originalName = req.file.originalname;

  try {
    // Register dataset entry in processing state
    let dataset;
    const datasetData = {
      name: originalName.split('.').slice(0, -1).join('.'),
      filename: filename,
      filepath: filepath,
      uploadedBy: req.user.id,
      status: 'processing'
    };

    if (isMongoConnected()) {
      dataset = new Dataset(datasetData);
      await dataset.save();
    } else {
      dataset = await fallbackDb.datasets.create(datasetData);
    }

    // Call FastAPI ML Service to extract statistics and profiles
    try {
      const response = await axios.post(`${ML_SERVICE_URL}/process`, { filepath });
      const summary = response.data;
      
      const columns = summary.columns.map(col => ({
        name: col.name,
        type: col.type,
        nullCount: col.nullCount,
        uniqueCount: col.uniqueCount,
        sampleValues: col.sampleValues,
        stats: col.stats
      }));

      const updateData = {
        rowCount: summary.rowCount,
        columnCount: summary.columnCount,
        columns: columns,
        summary: summary,
        status: 'active'
      };

      if (isMongoConnected()) {
        dataset = await Dataset.findByIdAndUpdate(dataset._id, updateData, { new: true });
      } else {
        dataset = await fallbackDb.datasets.findByIdAndUpdate(dataset._id, updateData);
      }

      res.status(201).json(dataset);
    } catch (mlErr) {
      console.error('ML service processing failed:', mlErr.message);
      // Mark as failed
      if (isMongoConnected()) {
        dataset = await Dataset.findByIdAndUpdate(dataset._id, { status: 'failed' }, { new: true });
      } else {
        dataset = await fallbackDb.datasets.findByIdAndUpdate(dataset._id, { status: 'failed' });
      }
      res.status(500).json({ message: 'Dataset processing failed inside ML service', dataset });
    }
  } catch (err) {
    console.error('Dataset upload controller error:', err.message);
    res.status(500).json({ message: 'Server error' });
  }
};

// 2. List Datasets
exports.getDatasets = async (req, res) => {
  try {
    let datasets;
    if (isMongoConnected()) {
      datasets = await Dataset.find({ uploadedBy: req.user.id }).sort({ createdAt: -1 });
    } else {
      datasets = await fallbackDb.datasets.find({ uploadedBy: req.user.id });
    }
    res.json(datasets);
  } catch (err) {
    console.error('Get datasets error:', err.message);
    res.status(500).json({ message: 'Server error' });
  }
};

// 3. Get Dataset Details
exports.getDatasetById = async (req, res) => {
  try {
    let dataset;
    if (isMongoConnected()) {
      dataset = await Dataset.findById(req.params.id);
    } else {
      dataset = await fallbackDb.datasets.findById(req.params.id);
    }

    if (!dataset) {
      return res.status(404).json({ message: 'Dataset not found' });
    }
    res.json(dataset);
  } catch (err) {
    console.error('Get dataset error:', err.message);
    res.status(500).json({ message: 'Server error' });
  }
};

// 4. Delete Dataset
exports.deleteDataset = async (req, res) => {
  try {
    let dataset;
    if (isMongoConnected()) {
      dataset = await Dataset.findById(req.params.id);
    } else {
      dataset = await fallbackDb.datasets.findById(req.params.id);
    }

    if (!dataset) {
      return res.status(404).json({ message: 'Dataset not found' });
    }

    // Delete physical file
    if (fs.existsSync(dataset.filepath)) {
      fs.unlinkSync(dataset.filepath);
    }

    // Delete associated db records
    if (isMongoConnected()) {
      await Dataset.findByIdAndDelete(req.params.id);
      await MLModel.deleteMany({ datasetId: req.params.id });
      await ChatHistory.deleteMany({ datasetId: req.params.id });
    } else {
      await fallbackDb.datasets.findByIdAndDelete(req.params.id);
      // Clean up fallback lists
      const data = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'data', 'db.json'), 'utf8'));
      data.models = data.models.filter(m => m.datasetId !== req.params.id.toString());
      data.chats = data.chats.filter(c => c.datasetId !== req.params.id.toString());
      fs.writeFileSync(path.join(__dirname, '..', 'data', 'db.json'), JSON.stringify(data, null, 2));
    }

    res.json({ message: 'Dataset and associated models/chats deleted successfully' });
  } catch (err) {
    console.error('Delete dataset error:', err.message);
    res.status(500).json({ message: 'Server error' });
  }
};

// 5. Rename Dataset
exports.renameDataset = async (req, res) => {
  const { name } = req.body;
  if (!name) return res.status(400).json({ message: 'Name is required' });

  try {
    let dataset;
    if (isMongoConnected()) {
      dataset = await Dataset.findByIdAndUpdate(req.params.id, { name }, { new: true });
    } else {
      dataset = await fallbackDb.datasets.findByIdAndUpdate(req.params.id, { name });
    }

    if (!dataset) {
      return res.status(404).json({ message: 'Dataset not found' });
    }
    res.json(dataset);
  } catch (err) {
    console.error('Rename dataset error:', err.message);
    res.status(500).json({ message: 'Server error' });
  }
};

// 6. Dataset AI Chat Endpoints (Two-Phase Query Loop)
exports.chatWithDataset = async (req, res) => {
  const { message } = req.body;
  if (!message) return res.status(400).json({ message: 'Message is required' });

  try {
    let dataset;
    if (isMongoConnected()) {
      dataset = await Dataset.findById(req.params.id);
    } else {
      dataset = await fallbackDb.datasets.findById(req.params.id);
    }

    if (!dataset) {
      return res.status(404).json({ message: 'Dataset not found' });
    }

    // Fetch recent chat history to provide memory context to the chatbot
    let chatRecord;
    if (isMongoConnected()) {
      chatRecord = await ChatHistory.findOne({ datasetId: dataset._id, userId: req.user.id });
    } else {
      chatRecord = await fallbackDb.chats.findOne({ datasetId: dataset._id, userId: req.user.id });
    }
    const previousChatHistory = chatRecord ? (chatRecord.messages || []) : [];

    // Phase 1: Call LLM to parse natural language to structured query spec (passing history for context)
    const querySpec = await LLMService.generateQuerySpec(message, dataset, previousChatHistory);
    
    // Phase 2: Execute pandas query on Python ML Service
    let queryResults;
    try {
      const response = await axios.post(`${ML_SERVICE_URL}/query`, {
        filepath: dataset.filepath,
        query_spec: querySpec
      });
      queryResults = response.data;
    } catch (queryErr) {
      console.error('FastAPI query execution failed, querySpec was:', querySpec, 'Error:', queryErr.message);
      queryResults = [];
    }

    // Phase 3: Send query results back to LLM to formulate conversational answer (passing history for context)
    const answer = await LLMService.generateAnswer(message, querySpec, queryResults, dataset, previousChatHistory);

    // Save Chat History
    const chatMsgUser = { role: 'user', content: message, timestamp: new Date() };
    const chatMsgAssist = { role: 'assistant', content: answer, timestamp: new Date() };

    let chatHistory;
    if (isMongoConnected()) {
      chatHistory = await ChatHistory.findOneAndUpdate(
        { datasetId: dataset._id, userId: req.user.id },
        { $push: { messages: { $each: [chatMsgUser, chatMsgAssist] } } },
        { new: true, upsert: true }
      );
    } else {
      await fallbackDb.chats.findOneAndUpdate(
        { datasetId: dataset._id, userId: req.user.id },
        { $push: { messages: chatMsgUser } }
      );
      chatHistory = await fallbackDb.chats.findOneAndUpdate(
        { datasetId: dataset._id, userId: req.user.id },
        { $push: { messages: chatMsgAssist } }
      );
    }

    res.json({
      answer,
      querySpec,
      queryResults,
      chatHistory
    });
  } catch (err) {
    console.error('Chat error:', err.message);
    res.status(500).json({ message: 'Server error during chat advisory execution' });
  }
};

exports.getChatHistory = async (req, res) => {
  try {
    let chat;
    if (isMongoConnected()) {
      chat = await ChatHistory.findOne({ datasetId: req.params.id, userId: req.user.id });
    } else {
      chat = await fallbackDb.chats.findOne({ datasetId: req.params.id, userId: req.user.id });
    }

    if (!chat) {
      return res.json({ messages: [] });
    }
    res.json(chat);
  } catch (err) {
    console.error('Get chat history error:', err.message);
    res.status(500).json({ message: 'Server error' });
  }
};

// 7. Machine Learning Modeling (FastAPI Model Studio)
exports.trainModel = async (req, res) => {
  const { targetVariable, taskType, dateColumn, features } = req.body;
  if (!targetVariable) return res.status(400).json({ message: 'Target variable is required' });

  try {
    let dataset;
    if (isMongoConnected()) {
      dataset = await Dataset.findById(req.params.id);
    } else {
      dataset = await fallbackDb.datasets.findById(req.params.id);
    }

    if (!dataset) {
      return res.status(404).json({ message: 'Dataset not found' });
    }

    const modelId = `model_${Math.random().toString(36).substring(2, 9)}`;

    // Call FastAPI to preprocess, train and evaluate
    try {
      const response = await axios.post(`${ML_SERVICE_URL}/train`, {
        filepath: dataset.filepath,
        target_col: targetVariable,
        task_type: taskType || 'auto',
        date_col: dateColumn || null,
        features: features || null,
        model_id: modelId
      });

      const trainResult = response.data;
      
      const modelPath = path.resolve(path.join('..', 'models', `${modelId}.joblib`));

      const newModelData = {
        datasetId: dataset._id,
        targetVariable: targetVariable,
        taskType: trainResult.task_type,
        metrics: trainResult.metrics,
        featureImportance: trainResult.feature_importances,
        modelPath: modelPath,
        trainedBy: req.user.id
      };

      let mlModel;
      if (isMongoConnected()) {
        mlModel = new MLModel(newModelData);
        await mlModel.save();
      } else {
        mlModel = await fallbackDb.models.create(newModelData);
      }

      res.status(201).json(mlModel);
    } catch (trainErr) {
      console.error('ML service training failed:', trainErr.message);
      res.status(500).json({ message: 'Model training failed inside Python service: ' + (trainErr.response?.data?.detail || trainErr.message) });
    }
  } catch (err) {
    console.error('Model training error:', err.message);
    res.status(500).json({ message: 'Server error' });
  }
};

exports.getModels = async (req, res) => {
  try {
    let models;
    if (isMongoConnected()) {
      models = await MLModel.find({ datasetId: req.params.id }).sort({ createdAt: -1 });
    } else {
      models = await fallbackDb.models.find({ datasetId: req.params.id });
    }
    res.json(models);
  } catch (err) {
    console.error('Get models error:', err.message);
    res.status(500).json({ message: 'Server error' });
  }
};

exports.predict = async (req, res) => {
  const { modelId, inputData } = req.body;
  if (!modelId || !inputData) return res.status(400).json({ message: 'Model ID and input features data are required' });

  try {
    let model;
    if (isMongoConnected()) {
      model = await MLModel.findById(modelId);
    } else {
      model = await fallbackDb.models.findById(modelId);
    }

    if (!model) return res.status(404).json({ message: 'Model record not found' });

    const response = await axios.post(`${ML_SERVICE_URL}/predict`, {
      model_path: model.modelPath,
      input_data: Array.isArray(inputData) ? inputData : [inputData]
    });

    res.json(response.data);
  } catch (err) {
    console.error('Prediction failed:', err.message);
    res.status(500).json({ message: 'Prediction query failed: ' + (err.response?.data?.detail || err.message) });
  }
};

// 8. PDF Report Generator (Using PDFKit)
exports.generateReport = async (req, res) => {
  try {
    let dataset;
    if (isMongoConnected()) {
      dataset = await Dataset.findById(req.params.id);
    } else {
      dataset = await fallbackDb.datasets.findById(req.params.id);
    }

    if (!dataset) {
      return res.status(404).json({ message: 'Dataset not found' });
    }

    // Get models for this dataset to report their evaluation scores
    let models;
    if (isMongoConnected()) {
      models = await MLModel.find({ datasetId: dataset._id });
    } else {
      models = await fallbackDb.models.find({ datasetId: dataset._id });
    }

    // Determine target column and date column for charts
    let target_col = null;
    let date_col = null;
    
    if (models.length > 0) {
      target_col = models[0].targetVariable;
      date_col = models.find(m => m.taskType === 'forecast')?.date_col || dataset.columns.find(c => c.type === 'datetime')?.name || null;
    } else {
      target_col = dataset.columns.find(c => c.type === 'numeric')?.name || null;
      date_col = dataset.columns.find(c => c.type === 'datetime')?.name || null;
    }

    const reportsDir = path.resolve(path.join('..', 'reports'));
    
    // 1. Generate chart images via FastAPI
    let charts = { correlationChart: null, distributionChart: null, trendChart: null };
    try {
      const chartRes = await axios.post(`${ML_SERVICE_URL}/generate-charts`, {
        filepath: dataset.filepath,
        dataset_id: dataset._id.toString(),
        date_col: date_col,
        target_col: target_col,
        output_dir: reportsDir
      });
      charts = chartRes.data;
    } catch (chartErr) {
      console.error('Report chart rendering failed in FastAPI, proceeding text-only:', chartErr.message);
    }

    // 2. Generate AI insights for executive summary
    const aiInsights = await LLMService.generateReportInsights(dataset, models);

    // 3. Compile PDF using PDFKit
    const doc = new PDFDocument({ margin: 50, size: 'A4' });
    
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename=AI_Advisor_Report_${dataset.name}.pdf`);
    
    doc.pipe(res);

    // Cover Page
    doc.rect(0, 0, doc.page.width, doc.page.height).fill('#0F172A'); // Dark theme cover page
    
    doc.fillColor('#10B981').fontSize(14).font('Helvetica-Bold').text('ENTERPRISE INTELLIGENT ANALYTICS', 50, 200);
    doc.fillColor('#FFFFFF').fontSize(28).text('AI Business Advisor Report', 50, 230);
    doc.fillColor('#94A3B8').fontSize(16).font('Helvetica').text(`Dataset: ${dataset.name}`, 50, 285);
    
    doc.rect(50, 320, 120, 4).fill('#10B981');
    
    doc.fillColor('#64748B').fontSize(10).text('Generated by Antigravity Intelligent Agent System', 50, doc.page.height - 100);
    doc.text(`Date: ${new Date().toLocaleDateString()}`, 50, doc.page.height - 85);
    
    // Add page
    doc.addPage().fillColor('#000000'); // Standard white page with black text
    
    // Page Header
    const addHeader = (title) => {
      doc.fillColor('#0F172A').fontSize(18).font('Helvetica-Bold').text(title, 50, 40);
      doc.rect(50, 65, doc.page.width - 100, 1).fill('#E2E8F0');
      doc.moveDown(2);
    };

    const addFooter = (pageNum) => {
      doc.fillColor('#94A3B8').fontSize(8).font('Helvetica').text(`AI Business Advisor Analytics Report | Page ${pageNum}`, 50, doc.page.height - 40, { align: 'center' });
    };

    // --- PAGE 2: EXECUTIVE SUMMARY ---
    addHeader('Executive Summary & Recommendations');
    doc.font('Helvetica').fontSize(10).fillColor('#334155');
    
    // Format LLM text nicely
    const sections = aiInsights.split(/(EXECUTIVE SUMMARY|STRATEGIC RECOMMENDATIONS):?/i);
    let execText = aiInsights;
    let recsText = '';
    
    if (sections.length >= 3) {
      execText = sections[2].trim();
      recsText = sections[sections.length - 1].trim();
    }
    
    doc.font('Helvetica-Bold').fontSize(12).text('Strategic Summary', 50, 90);
    doc.font('Helvetica').fontSize(10).text(execText, 50, 110, { width: doc.page.width - 100, align: 'justify' });
    
    doc.moveDown(2);
    doc.font('Helvetica-Bold').fontSize(12).text('AI-Generated Business Actions');
    doc.moveDown(0.5);
    
    doc.font('Helvetica').fontSize(10);
    if (recsText) {
      const bullets = recsText.split('\n').filter(b => b.trim());
      bullets.forEach(b => {
        const cleanBullet = b.replace(/^-\s*\*?\*?|^\d+\.\s*\*?\*?/, '').replace(/\*\*/g, '');
        doc.text(`•  ${cleanBullet}`, { width: doc.page.width - 100 });
        doc.moveDown(0.5);
      });
    } else {
      doc.text('•  Increase sales operations in high margin business sectors.\n•  Deploy machine learning predictive inventories.\n•  Re-segment transaction logs to capture structural margins.', { width: doc.page.width - 100 });
    }
    
    addFooter(2);

    // --- PAGE 3: DATASET STATISTICAL OVERVIEW ---
    doc.addPage();
    addHeader('Dataset Statistical Profiles');
    
    doc.font('Helvetica-Bold').fontSize(12).fillColor('#0F172A').text('Metadata Summary');
    doc.font('Helvetica').fontSize(10).fillColor('#334155');
    doc.text(`- Row Count: ${dataset.rowCount} rows`);
    doc.text(`- Column Count: ${dataset.columnCount} features`);
    doc.text(`- Integrity: ${dataset.summary.duplicates || 0} duplicates detected`);
    doc.moveDown(1.5);
    
    doc.font('Helvetica-Bold').fontSize(12).fillColor('#0F172A').text('Features & Detected Types');
    doc.moveDown(0.5);
    
    // Basic Table Grid using manual drawing
    let yPos = doc.y;
    doc.font('Helvetica-Bold').fontSize(9).text('Feature Name', 55, yPos);
    doc.text('Type', 200, yPos);
    doc.text('Null Count', 320, yPos);
    doc.text('Unique Values', 430, yPos);
    
    doc.rect(50, yPos + 15, doc.page.width - 100, 1).fill('#CBD5E1');
    yPos += 25;
    
    doc.font('Helvetica').fontSize(9);
    dataset.columns.slice(0, 15).forEach((col) => {
      if (yPos > doc.page.height - 80) {
        doc.addPage();
        addHeader('Dataset Statistical Profiles (Continued)');
        yPos = doc.y;
      }
      doc.text(col.name, 55, yPos);
      doc.text(col.type.toUpperCase(), 200, yPos);
      doc.text(col.nullCount.toString(), 320, yPos);
      doc.text(col.uniqueCount.toString(), 430, yPos);
      yPos += 18;
    });

    addFooter(3);

    // --- PAGE 4: DETAILED VARIABLE METRICS ---
    doc.addPage();
    addHeader('Detailed Variable Metrics & Audit');
    
    // Numeric Column Metrics
    const numericColumns = dataset.columns.filter(c => c.type === 'numeric');
    if (numericColumns.length > 0) {
      doc.font('Helvetica-Bold').fontSize(12).fillColor('#0F172A').text('Numerical Variables Descriptive Statistics');
      doc.moveDown(0.5);
      
      let yPos = doc.y;
      doc.font('Helvetica-Bold').fontSize(8).fillColor('#1E293B');
      doc.text('Column Name', 55, yPos);
      doc.text('Mean', 180, yPos);
      doc.text('Min', 250, yPos);
      doc.text('Max', 320, yPos);
      doc.text('Std Dev', 390, yPos);
      doc.text('Outliers', 460, yPos);
      
      doc.rect(50, yPos + 12, doc.page.width - 100, 1).fill('#CBD5E1');
      yPos += 20;
      
      doc.font('Helvetica').fontSize(8).fillColor('#334155');
      numericColumns.slice(0, 10).forEach(col => {
        const stats = col.stats || {};
        const outlierInfo = dataset.summary.outliers?.[col.name] || { outlierCount: 0, percentage: 0 };
        
        doc.text(col.name, 55, yPos);
        doc.text(stats.mean !== undefined ? Number(stats.mean).toFixed(2) : 'N/A', 180, yPos);
        doc.text(stats.min !== undefined ? Number(stats.min).toFixed(2) : 'N/A', 250, yPos);
        doc.text(stats.max !== undefined ? Number(stats.max).toFixed(2) : 'N/A', 320, yPos);
        doc.text(stats.std !== undefined ? Number(stats.std).toFixed(2) : 'N/A', 390, yPos);
        doc.text(`${outlierInfo.outlierCount} (${outlierInfo.percentage ? Number(outlierInfo.percentage).toFixed(1) : 0}%)`, 460, yPos);
        
        yPos += 15;
      });
      doc.moveDown(2);
    }
    
    // Categorical Column Metrics
    const categoricalColumns = dataset.columns.filter(c => c.type === 'categorical' && c.stats?.top_values);
    if (categoricalColumns.length > 0) {
      if (doc.y > doc.page.height - 180) {
        doc.addPage();
        addHeader('Detailed Variable Metrics (Continued)');
      }
      
      doc.font('Helvetica-Bold').fontSize(12).fillColor('#0F172A').text('Categorical Variables Distribution Audit');
      doc.moveDown(0.5);
      
      let yPos = doc.y;
      doc.font('Helvetica-Bold').fontSize(8).fillColor('#1E293B');
      doc.text('Column Name', 55, yPos);
      doc.text('Unique Vals', 180, yPos);
      doc.text('Top Value Segment', 250, yPos);
      doc.text('Frequency', 390, yPos);
      doc.text('Percentage', 460, yPos);
      
      doc.rect(50, yPos + 12, doc.page.width - 100, 1).fill('#CBD5E1');
      yPos += 20;
      
      doc.font('Helvetica').fontSize(8).fillColor('#334155');
      categoricalColumns.slice(0, 10).forEach(col => {
        const topVal = Object.keys(col.stats.top_values)[0] || 'N/A';
        const topCount = col.stats.top_values[topVal] || 0;
        const pct = ((topCount / dataset.rowCount) * 100).toFixed(1);
        
        doc.text(col.name, 55, yPos);
        doc.text(col.uniqueCount.toString(), 180, yPos);
        doc.text(topVal.length > 25 ? topVal.slice(0, 22) + '...' : topVal, 250, yPos);
        doc.text(topCount.toString(), 390, yPos);
        doc.text(`${pct}%`, 460, yPos);
        
        yPos += 15;
      });
    }
    
    addFooter(4);

    // --- PAGE 5: VISUALIZATIONS ---
    doc.addPage();
    addHeader('Data Visualizations');
    
    let chartPlacements = 0;
    
    if (charts.distributionChart && fs.existsSync(charts.distributionChart)) {
      doc.font('Helvetica-Bold').fontSize(11).text('Feature Distributions', 50, 80);
      doc.image(charts.distributionChart, 50, 100, { width: 480, height: 220 });
      chartPlacements++;
    }

    if (charts.trendChart && fs.existsSync(charts.trendChart)) {
      doc.font('Helvetica-Bold').fontSize(11).text('Time-Series Overtime Trends', 50, 350);
      doc.image(charts.trendChart, 50, 370, { width: 480, height: 220 });
      chartPlacements++;
    }
    
    if (chartPlacements === 0) {
      doc.font('Helvetica').fontSize(12).text('Visualizations could not be rendered because python environment was compiling.', 50, 150);
    }
    
    addFooter(5);

    // --- PAGE 6: CORRELATION MAP ---
    if (charts.correlationChart && fs.existsSync(charts.correlationChart)) {
      doc.addPage();
      addHeader('Correlation Map & Correlation Matrix');
      doc.image(charts.correlationChart, 50, 80, { width: 480, height: 380 });
      addFooter(6);
    }

    doc.addPage();
    addHeader('Machine Learning Analytics');
    
    doc.font('Helvetica-Bold').fontSize(12).text('Trained Model Performance Evaluation');
    doc.moveDown(0.5);

    if (models.length === 0) {
      doc.font('Helvetica').fontSize(10).fillColor('#64748B').text('No machine learning models have been trained on this dataset yet. Setup predictive variables in the ML Studio tab of the application.', { width: doc.page.width - 100 });
    } else {
      models.forEach((m, idx) => {
        doc.font('Helvetica-Bold').fontSize(10).fillColor('#10B981').text(`Model #${idx+1}: XGBoost Model (${m.taskType.toUpperCase()})`);
        doc.font('Helvetica').fontSize(9).fillColor('#334155');
        doc.text(`- Target Variable: ${m.targetVariable}`);
        
        doc.text('Evaluation Metrics:');
        for (let metricName in m.metrics) {
          doc.text(`  •  ${metricName.toUpperCase()}: ${Number(m.metrics[metricName]).toFixed(4)}`);
        }
        
        doc.moveDown(1);
        
        // Show Top Features
        doc.font('Helvetica-Bold').fontSize(9).text('Top 5 Features of Influence:');
        const sortedFeatures = Object.entries(m.featureImportance || {})
          .sort((a, b) => b[1] - a[1])
          .slice(0, 5);
          
        sortedFeatures.forEach(([feat, val]) => {
          doc.font('Helvetica').text(`  - ${feat}: ${(val * 100).toFixed(2)}% influence`);
        });
        
        doc.moveDown(1.5);
      });
    }
    
    addFooter(doc.bufferedPageRange().count);

    doc.end();

  } catch (err) {
    console.error('Report compilation failed:', err.message);
    if (!res.headersSent) {
      res.status(500).json({ message: 'Server failed to generate report PDF' });
    }
  }
};
