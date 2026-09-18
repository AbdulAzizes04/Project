import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell } from 'recharts';
import { Brain, Cpu, Play, CheckCircle2, ChevronRight, Gauge, AlertCircle, Info, HelpCircle } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const MLStudio = ({ activeDataset }) => {
  const [targetCol, setTargetCol] = useState('');
  const [selectedFeatures, setSelectedFeatures] = useState([]);
  const [taskType, setTaskType] = useState('auto');
  const [dateCol, setDateCol] = useState('');
  
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState(null);
  
  const [training, setTraining] = useState(false);
  const [trainError, setTrainError] = useState('');
  const [trainSuccess, setTrainSuccess] = useState(false);

  // Prediction state
  const [predictInputs, setPredictInputs] = useState({});
  const [predictionResult, setPredictionResult] = useState(null);
  const [predicting, setPredicting] = useState(false);

  const columns = activeDataset?.columns || [];
  const numericCols = columns.filter(c => c.type === 'numeric').map(c => c.name);
  const dateCols = columns.filter(c => c.type === 'datetime').map(c => c.name);
  const featuresList = columns.map(c => c.name);

  useEffect(() => {
    if (activeDataset) {
      // Pick defaults
      setTargetCol(numericCols[0] || columns[0]?.name || '');
      setSelectedFeatures(columns.slice(1, 6).map(c => c.name));
      setDateCol(dateCols[0] || '');
      fetchModels();
    }
  }, [activeDataset]);

  const fetchModels = async () => {
    if (!activeDataset) return;
    try {
      const res = await axios.get(`${API_URL}/datasets/${activeDataset._id}/models`);
      setModels(res.data);
      if (res.data.length > 0) {
        setSelectedModel(res.data[0]);
      }
    } catch (err) {
      console.error('Error fetching models:', err);
    }
  };

  const toggleFeature = (feat) => {
    if (feat === targetCol) return;
    setSelectedFeatures(prev =>
      prev.includes(feat) ? prev.filter(f => f !== feat) : [...prev, feat]
    );
  };

  const handleTrain = async (e) => {
    e.preventDefault();
    if (!targetCol) return;

    setTraining(true);
    setTrainError('');
    setTrainSuccess(false);

    try {
      const res = await axios.post(`${API_URL}/datasets/${activeDataset._id}/train`, {
        targetVariable: targetCol,
        taskType: taskType,
        dateColumn: taskType === 'forecast' ? dateCol : null,
        features: selectedFeatures
      });

      setTrainSuccess(true);
      fetchModels();
      setSelectedModel(res.data);
    } catch (err) {
      console.error('Training failed:', err);
      setTrainError(err.response?.data?.message || 'Model training failed inside Python service.');
    } finally {
      setTraining(false);
    }
  };

  // Initialize prediction inputs when selected model changes
  useEffect(() => {
    if (selectedModel) {
      const inputs = {};
      const features = selectedModel.featureImportance ? Object.keys(selectedModel.featureImportance) : [];
      features.forEach(f => {
        inputs[f] = '';
      });
      setPredictInputs(inputs);
      setPredictionResult(null);
    }
  }, [selectedModel]);

  const handlePredictSubmit = async (e) => {
    e.preventDefault();
    if (!selectedModel) return;

    setPredicting(true);
    setPredictionResult(null);

    // Convert inputs values to float if they look like numbers
    const processedInputs = {};
    for (let key in predictInputs) {
      const val = predictInputs[key];
      processedInputs[key] = val === '' ? 0.0 : isNaN(val) ? val : parseFloat(val);
    }

    try {
      const res = await axios.post(`${API_URL}/datasets/${activeDataset._id}/predict`, {
        modelId: selectedModel._id,
        inputData: [processedInputs]
      });
      setPredictionResult(res.data.predictions[0]);
    } catch (err) {
      console.error('Prediction failed:', err);
      alert('Prediction query failed. Ensure all numerical columns are filled.');
    } finally {
      setPredicting(false);
    }
  };

  const featureImportanceChartData = selectedModel?.featureImportance
    ? Object.entries(selectedModel.featureImportance)
        .map(([name, value]) => ({ name, value: Number((value * 100).toFixed(2)) }))
        .slice(0, 10)
    : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight dark:text-white text-slate-800 flex items-center gap-2">
          Model Studio
          <Brain className="w-5 h-5 text-indigo-500" />
        </h1>
        <p className="text-sm dark:text-slate-400 text-slate-500">
          Build and query custom machine learning estimators directly from your dataset.
        </p>
      </div>

      {!activeDataset ? (
        <div className="glass-card p-12 text-center flex flex-col items-center justify-center min-h-[400px]">
          <Cpu className="w-14 h-14 text-slate-500 mb-4 animate-pulse" />
          <h3 className="text-lg font-bold dark:text-slate-200 text-slate-700">Studio Offline</h3>
          <p className="text-sm dark:text-slate-400 text-slate-500 max-w-sm mt-1">
            Upload a dataset or select an active dataset in the Dataset Workspace tab to load ML training studios.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Training Setup Panel */}
          <div className="lg:col-span-1 space-y-6">
            <div className="glass-card p-6">
              <h3 className="text-sm font-bold tracking-wider dark:text-slate-300 text-slate-700 uppercase mb-4 flex items-center gap-2">
                <Cpu className="w-4.5 h-4.5 text-indigo-500" /> Model Settings
              </h3>

              <form onSubmit={handleTrain} className="space-y-4">
                {/* Target Column */}
                <div>
                  <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Target Variable</label>
                  <select
                    value={targetCol}
                    onChange={(e) => {
                      setTargetCol(e.target.value);
                      setSelectedFeatures(prev => prev.filter(f => f !== e.target.value));
                    }}
                    className="w-full bg-slate-100 dark:bg-slate-900 border dark:border-slate-800 border-slate-200 text-slate-700 dark:text-slate-200 rounded-lg text-xs p-2.5 focus:outline-none focus:border-indigo-500 mt-1"
                  >
                    {featuresList.map((col, idx) => (
                      <option key={idx} value={col}>{col}</option>
                    ))}
                  </select>
                </div>

                {/* Task Type */}
                <div>
                  <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Modeling Task</label>
                  <select
                    value={taskType}
                    onChange={(e) => setTaskType(e.target.value)}
                    className="w-full bg-slate-100 dark:bg-slate-900 border dark:border-slate-800 border-slate-200 text-slate-700 dark:text-slate-200 rounded-lg text-xs p-2.5 focus:outline-none focus:border-indigo-500 mt-1"
                  >
                    <option value="auto">Auto-Detect Task</option>
                    <option value="classification">Classification (Categories)</option>
                    <option value="regression">Regression (Numbers)</option>
                    <option value="forecast">Forecasting (Time-Series)</option>
                  </select>
                </div>

                {/* Date Column (Time-Series forecasting) */}
                {taskType === 'forecast' && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="space-y-1"
                  >
                    <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Date/Time Column</label>
                    <select
                      value={dateCol}
                      onChange={(e) => setDateCol(e.target.value)}
                      className="w-full bg-slate-100 dark:bg-slate-900 border dark:border-slate-800 border-slate-200 text-slate-700 dark:text-slate-200 rounded-lg text-xs p-2.5 focus:outline-none focus:border-indigo-500 mt-1"
                    >
                      <option value="">-- Choose Date Column --</option>
                      {dateCols.map((col, idx) => (
                        <option key={idx} value={col}>{col}</option>
                      ))}
                    </select>
                  </motion.div>
                )}

                {/* Features Selector */}
                <div>
                  <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Input Predictor Features</label>
                  <div className="max-h-40 overflow-y-auto border dark:border-slate-800 border-slate-200 rounded-lg p-2.5 space-y-1.5 mt-1 dark:bg-slate-900/40 bg-slate-50">
                    {featuresList.map((col) => (
                      <div
                        key={col}
                        onClick={() => toggleFeature(col)}
                        className={`flex items-center gap-2 cursor-pointer p-1 rounded text-xs transition-colors ${
                          col === targetCol
                            ? 'opacity-40 pointer-events-none'
                            : 'hover:bg-slate-800/10 dark:hover:bg-slate-800'
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={selectedFeatures.includes(col) && col !== targetCol}
                          readOnly
                          className="rounded text-indigo-500"
                        />
                        <span className="dark:text-slate-300 text-slate-600 truncate">{col}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={training || !targetCol}
                  className="w-full bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl py-3 font-semibold text-xs shadow-lg shadow-indigo-600/20 active:scale-[0.98] transition-all disabled:opacity-50 disabled:pointer-events-none flex items-center justify-center gap-2 mt-4"
                >
                  {training ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Training Estimators...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 fill-current" />
                      Train XGBoost Model
                    </>
                  )}
                </button>
              </form>

              {/* Status Display */}
              {trainSuccess && (
                <div className="bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 p-4 rounded-xl text-xs flex items-start gap-2 mt-4 animate-fade-in">
                  <CheckCircle2 className="w-4.5 h-4.5 shrink-0 mt-0.5" />
                  <span>Model trained successfully! Metrics compiled and pipeline serialized to disk.</span>
                </div>
              )}

              {trainError && (
                <div className="bg-rose-500/15 border border-rose-500/30 text-rose-400 p-4 rounded-xl text-xs flex items-start gap-2 mt-4">
                  <AlertCircle className="w-4.5 h-4.5 shrink-0 mt-0.5" />
                  <span>{trainError}</span>
                </div>
              )}
            </div>

            {/* Model Registry List */}
            {models.length > 0 && (
              <div className="glass-card p-6">
                <h3 className="text-xs font-bold tracking-wider dark:text-slate-300 text-slate-700 uppercase mb-4">Saved Models List</h3>
                <div className="space-y-2">
                  {models.map(m => (
                    <div
                      key={m._id}
                      onClick={() => setSelectedModel(m)}
                      className={`p-3 rounded-lg border text-left cursor-pointer transition-all flex items-center justify-between ${
                        selectedModel && selectedModel._id === m._id
                          ? 'dark:bg-indigo-600/10 bg-indigo-50 dark:border-indigo-500/40 border-indigo-200'
                          : 'dark:bg-slate-900/50 bg-white dark:border-slate-800 border-slate-200 dark:hover:border-slate-700 hover:border-slate-300'
                      }`}
                    >
                      <div>
                        <p className="text-xs font-bold dark:text-slate-200 text-slate-700 uppercase">
                          {m.taskType} • {m.targetVariable}
                        </p>
                        <p className="text-[10px] text-slate-400 mt-0.5">
                          Trained {new Date(m.createdAt).toLocaleDateString()}
                        </p>
                      </div>
                      <ChevronRight className="w-4 h-4 text-slate-400" />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Model Statistics Panel */}
          <div className="lg:col-span-2 space-y-6">
            {selectedModel ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-6"
              >
                {/* Metrics Row */}
                <div className="glass-card p-6">
                  <h3 className="text-sm font-bold dark:text-white text-slate-800 uppercase tracking-wider mb-4 flex items-center gap-1.5">
                    <Gauge className="w-4.5 h-4.5 text-indigo-500" /> Model Performance Metrics
                  </h3>

                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-6">
                    {Object.entries(selectedModel.metrics).map(([metricName, metricValue]) => (
                      <div
                        key={metricName}
                        className="p-4 bg-slate-900/50 border dark:border-slate-800 border-slate-100 rounded-xl relative overflow-hidden text-center"
                      >
                        <p className="text-[9px] uppercase font-bold tracking-wider dark:text-slate-400 text-slate-500">{metricName}</p>
                        <p className="text-2xl font-bold dark:text-white text-slate-800 mt-2">
                          {Number(metricValue).toFixed(4)}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Feature Importance Plot */}
                {featureImportanceChartData.length > 0 && (
                  <div className="glass-card p-6">
                    <h3 className="text-sm font-bold dark:text-white text-slate-800 uppercase tracking-wider mb-6">Feature Importance Profile</h3>
                    <div className="h-[260px]">
                      <ResponsiveContainer width="100%" h="100%">
                        <BarChart
                          data={featureImportanceChartData}
                          layout="vertical"
                          margin={{ left: 20, right: 20 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.1} />
                          <XAxis type="number" stroke="#64748B" fontSize={10} unit="%" />
                          <YAxis type="category" dataKey="name" stroke="#64748B" fontSize={10} tickLine={false} />
                          <Tooltip formatter={(value) => [`${value}%`, 'Importance']} />
                          <Bar dataKey="value" fill="#6366F1" radius={[0, 4, 4, 0]}>
                            {featureImportanceChartData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                )}

                {/* Live Simulator Prediction */}
                <div className="glass-card p-6">
                  <h3 className="text-sm font-bold dark:text-white text-slate-800 uppercase tracking-wider mb-4">Interactive Prediction Simulator</h3>
                  <p className="text-xs dark:text-slate-400 text-slate-500 mb-6">
                    Input customized feature values below to fetch live predictions from the serialized model pipeline.
                  </p>

                  <form onSubmit={handlePredictSubmit} className="space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {Object.keys(predictInputs).map((feat) => (
                        <div key={feat} className="space-y-1">
                          <label className="text-[10px] font-bold dark:text-slate-400 text-slate-500 truncate block">{feat}</label>
                          <input
                            type="text"
                            required
                            value={predictInputs[feat]}
                            onChange={(e) => setPredictInputs({ ...predictInputs, [feat]: e.target.value })}
                            placeholder="Enter value"
                            className="w-full bg-slate-100 dark:bg-slate-900 border dark:border-slate-800 border-slate-200 text-slate-700 dark:text-slate-200 rounded-lg text-xs p-2.5 focus:outline-none focus:border-indigo-500"
                          />
                        </div>
                      ))}
                    </div>

                    <div className="flex flex-col sm:flex-row items-center gap-4 pt-4 border-t dark:border-slate-800 border-slate-200">
                      <button
                        type="submit"
                        disabled={predicting || Object.keys(predictInputs).length === 0}
                        className="w-full sm:w-auto bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl px-6 py-2.5 font-semibold text-xs shadow-lg shadow-emerald-600/20 transition-all disabled:opacity-50 disabled:pointer-events-none flex items-center justify-center gap-2"
                      >
                        {predicting ? 'Querying Pipeline...' : 'Generate Prediction'}
                      </button>

                      {predictionResult !== null && (
                        <div className="flex-1 p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl text-center sm:text-left flex items-center gap-2 justify-center sm:justify-start">
                          <span className="text-xs dark:text-slate-400 text-slate-500">Predicted Output:</span>
                          <span className="text-base font-bold text-indigo-400">{Number(predictionResult).toFixed(4)}</span>
                        </div>
                      )}
                    </div>
                  </form>
                </div>
              </motion.div>
            ) : (
              <div className="glass-card p-6 h-full flex flex-col items-center justify-center min-h-[400px]">
                <Cpu className="w-12 h-12 text-slate-600 dark:text-slate-500 mb-3" />
                <h3 className="text-base font-bold dark:text-slate-200 text-slate-700">No Model Selected</h3>
                <p className="text-xs dark:text-slate-400 text-slate-500 text-center max-w-sm mt-1">
                  Select a trained model from the registry on the left sidebar to view statistics profiles or make live predictions, or run a new training task above.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

const COLORS = ['#6366F1', '#10B981', '#F59E0B', '#EF4444', '#EC4899', '#8B5CF6'];

export default MLStudio;
