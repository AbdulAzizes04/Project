import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Upload, Database, FileSpreadsheet, Trash2, Edit3, CheckCircle, AlertTriangle, Loader, Info, HelpCircle } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const Datasets = ({ activeDataset, setActiveDataset }) => {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [renamingId, setRenamingId] = useState(null);
  const [renamingName, setRenamingName] = useState('');

  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_URL}/datasets`);
      setDatasets(res.data);
      if (res.data.length > 0 && !activeDataset) {
        // Set the most recent active dataset
        const active = res.data.find(d => d.status === 'active');
        if (active) setActiveDataset(active);
      }
    } catch (err) {
      console.error('Error fetching datasets:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file) => {
    if (!file) return;
    
    // Check file format
    const ext = file.name.split('.').pop().toLowerCase();
    if (ext !== 'csv' && ext !== 'xlsx' && ext !== 'xls') {
      setUploadError('Only CSV or Excel (.xlsx, .xls) files are supported.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    setUploadError('');
    setUploadProgress(10);

    try {
      // Simulate progress
      const interval = setInterval(() => {
        setUploadProgress(prev => (prev < 90 ? prev + 10 : prev));
      }, 300);

      const res = await axios.post(`${API_URL}/datasets/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      clearInterval(interval);
      setUploadProgress(100);
      setTimeout(() => {
        setUploading(false);
        setUploadProgress(0);
        fetchDatasets();
        if (res.data && res.data.status === 'active') {
          setActiveDataset(res.data);
        }
      }, 500);
    } catch (err) {
      console.error('Upload failed:', err);
      setUploadError(err.response?.data?.message || 'Failed to process dataset. Ensure column names are clean and file size is reasonable.');
      setUploading(false);
    }
  };

  const onDragOver = (e) => {
    e.preventDefault();
  };

  const onDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this dataset? All trained ML models and chat logs will be lost.')) return;
    
    try {
      await axios.delete(`${API_URL}/datasets/${id}`);
      if (activeDataset && activeDataset._id === id) {
        setActiveDataset(null);
      }
      fetchDatasets();
    } catch (err) {
      console.error('Delete failed:', err);
    }
  };

  const handleRename = async (id, e) => {
    e.stopPropagation();
    if (!renamingName.trim()) return;

    try {
      await axios.patch(`${API_URL}/datasets/${id}`, { name: renamingName });
      setRenamingId(null);
      setRenamingName('');
      fetchDatasets();
    } catch (err) {
      console.error('Rename failed:', err);
    }
  };

  const startRename = (id, name, e) => {
    e.stopPropagation();
    setRenamingId(id);
    setRenamingName(name);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight dark:text-white text-slate-800">Dataset Workspace</h1>
        <p className="text-sm dark:text-slate-400 text-slate-500">Upload, profile, and inspect your business files.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload & List Column */}
        <div className="lg:col-span-1 space-y-6">
          {/* Drag & Drop File Zone */}
          <div
            onDragOver={onDragOver}
            onDrop={onDrop}
            onClick={() => fileInputRef.current.click()}
            className="border-2 border-dashed dark:border-slate-700 border-slate-300 dark:hover:border-indigo-500 hover:border-indigo-400 dark:bg-slate-800/40 bg-slate-50 rounded-xl p-8 text-center cursor-pointer transition-all flex flex-col items-center justify-center min-h-[220px]"
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={(e) => handleFileUpload(e.target.files[0])}
              className="hidden"
              accept=".csv, .xlsx, .xls"
            />
            {uploading ? (
              <div className="space-y-3">
                <Loader className="w-10 h-10 text-indigo-500 animate-spin mx-auto" />
                <p className="text-sm font-semibold dark:text-slate-300 text-slate-600">Processing & Analyzing Data...</p>
                <div className="w-32 bg-slate-700 h-1.5 rounded-full mx-auto overflow-hidden">
                  <div 
                    className="bg-indigo-500 h-full rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="p-3 bg-indigo-500/10 text-indigo-500 rounded-2xl w-fit mx-auto">
                  <Upload className="w-8 h-8" />
                </div>
                <div>
                  <p className="text-sm font-semibold dark:text-slate-200 text-slate-700">Drag & drop your files here</p>
                  <p className="text-xs dark:text-slate-400 text-slate-500 mt-1">Supports CSV, Excel (.xlsx, .xls)</p>
                </div>
              </div>
            )}
          </div>

          {/* Upload error display */}
          {uploadError && (
            <div className="bg-rose-500/10 border border-rose-500/30 text-rose-400 p-4 rounded-xl text-xs flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{uploadError}</span>
            </div>
          )}

          {/* Dataset Inventory Card */}
          <div className="glass-card p-6">
            <h3 className="text-sm font-bold tracking-wider dark:text-slate-300 text-slate-700 uppercase mb-4 flex items-center gap-2">
              <Database className="w-4 h-4 text-indigo-500" />
              Dataset History
            </h3>

            {loading && datasets.length === 0 ? (
              <div className="py-6 flex items-center justify-center">
                <Loader className="w-6 h-6 text-slate-400 animate-spin" />
              </div>
            ) : datasets.length === 0 ? (
              <p className="text-xs dark:text-slate-500 text-slate-400 text-center py-6">No datasets loaded yet.</p>
            ) : (
              <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
                {datasets.map((d) => (
                  <div
                    key={d._id}
                    onClick={() => d.status === 'active' && setActiveDataset(d)}
                    className={`p-3 rounded-lg border text-left cursor-pointer transition-all flex items-center justify-between ${
                      activeDataset && activeDataset._id === d._id
                        ? 'dark:bg-indigo-600/10 bg-indigo-50 dark:border-indigo-500/40 border-indigo-200'
                        : 'dark:bg-slate-900/50 bg-white dark:border-slate-800 border-slate-200 dark:hover:border-slate-700 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center gap-3 overflow-hidden">
                      <FileSpreadsheet className={`w-5 h-5 shrink-0 ${d.status === 'active' ? 'text-emerald-500' : 'text-slate-400'}`} />
                      <div className="overflow-hidden">
                        {renamingId === d._id ? (
                          <input
                            type="text"
                            value={renamingName}
                            onChange={(e) => setRenamingName(e.target.value)}
                            onClick={(e) => e.stopPropagation()}
                            onKeyDown={(e) => e.key === 'Enter' && handleRename(d._id, e)}
                            className="bg-slate-800 border border-slate-700 text-white rounded text-xs px-2 py-0.5 focus:outline-none focus:border-indigo-500"
                            autoFocus
                          />
                        ) : (
                          <p className="text-xs font-semibold dark:text-slate-200 text-slate-700 truncate">{d.name}</p>
                        )}
                        <p className="text-[10px] dark:text-slate-400 text-slate-500 mt-0.5">
                          {d.rowCount} rows • {d.status.toUpperCase()}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-1 shrink-0">
                      {renamingId === d._id ? (
                        <button
                          onClick={(e) => handleRename(d._id, e)}
                          className="p-1 text-emerald-400 hover:bg-emerald-500/15 rounded"
                        >
                          <CheckCircle className="w-3.5 h-3.5" />
                        </button>
                      ) : (
                        <button
                          onClick={(e) => startRename(d._id, d.name, e)}
                          className="p-1 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded"
                        >
                          <Edit3 className="w-3.5 h-3.5" />
                        </button>
                      )}
                      <button
                        onClick={(e) => handleDelete(d._id, e)}
                        className="p-1 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Dataset Schema Columns Column */}
        <div className="lg:col-span-2">
          {activeDataset ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="glass-card p-6 h-full flex flex-col"
            >
              {/* Active Header */}
              <div className="flex items-center justify-between pb-4 border-b dark:border-slate-800 border-slate-200 mb-6">
                <div>
                  <h2 className="text-lg font-bold dark:text-white text-slate-800">{activeDataset.name}</h2>
                  <p className="text-xs dark:text-slate-400 text-slate-500 mt-0.5">
                    Dataset Schema Profiling ({(activeDataset.columns || []).length} columns identified)
                  </p>
                </div>
                <span className="px-2.5 py-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[10px] font-bold rounded-full uppercase tracking-wider">
                  Active
                </span>
              </div>

              {/* Data Summary Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
                <div className="p-4 dark:bg-slate-900/60 bg-slate-50 border dark:border-slate-800 border-slate-100 rounded-xl">
                  <p className="text-[10px] uppercase font-bold tracking-wider dark:text-slate-400 text-slate-500">Total Rows</p>
                  <p className="text-xl font-bold dark:text-white text-slate-800 mt-1">{(activeDataset.rowCount || 0).toLocaleString()}</p>
                </div>
                <div className="p-4 dark:bg-slate-900/60 bg-slate-50 border dark:border-slate-800 border-slate-100 rounded-xl">
                  <p className="text-[10px] uppercase font-bold tracking-wider dark:text-slate-400 text-slate-500">Columns count</p>
                  <p className="text-xl font-bold dark:text-white text-slate-800 mt-1">{activeDataset.columnCount || (activeDataset.columns || []).length}</p>
                </div>
                <div className="p-4 dark:bg-slate-900/60 bg-slate-50 border dark:border-slate-800 border-slate-100 rounded-xl">
                  <p className="text-[10px] uppercase font-bold tracking-wider dark:text-slate-400 text-slate-500">Duplicates</p>
                  <p className="text-xl font-bold dark:text-white text-slate-800 mt-1">{activeDataset.summary?.duplicates || 0}</p>
                </div>
                <div className="p-4 dark:bg-slate-900/60 bg-slate-50 border dark:border-slate-800 border-slate-100 rounded-xl">
                  <p className="text-[10px] uppercase font-bold tracking-wider dark:text-slate-400 text-slate-500">Missing values</p>
                  <p className="text-xl font-bold dark:text-white text-slate-800 mt-1">
                    {(activeDataset.columns || []).reduce((sum, c) => sum + (c.nullCount || 0), 0).toLocaleString()}
                  </p>
                </div>
              </div>

              {/* Columns Table */}
              <div className="flex-1 overflow-x-auto min-h-[300px]">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b dark:border-slate-800 border-slate-200">
                      <th className="pb-3 text-xs font-bold uppercase tracking-wider dark:text-slate-400 text-slate-500">Column Name</th>
                      <th className="pb-3 text-xs font-bold uppercase tracking-wider dark:text-slate-400 text-slate-500 pl-4">Type</th>
                      <th className="pb-3 text-xs font-bold uppercase tracking-wider dark:text-slate-400 text-slate-500 pl-4">Missing</th>
                      <th className="pb-3 text-xs font-bold uppercase tracking-wider dark:text-slate-400 text-slate-500 pl-4">Sample Values</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(activeDataset.columns || []).map((col, idx) => (
                      <tr
                        key={idx}
                        className="border-b dark:border-slate-800/40 border-slate-100 hover:bg-slate-900/10 dark:hover:bg-slate-800/20"
                      >
                        <td className="py-3 text-xs font-semibold dark:text-slate-200 text-slate-700">{col.name}</td>
                        <td className="py-3 pl-4">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                            col.type === 'numeric' 
                              ? 'bg-blue-500/10 text-blue-400' 
                              : col.type === 'datetime'
                              ? 'bg-emerald-500/10 text-emerald-400'
                              : 'bg-indigo-500/10 text-indigo-400'
                          }`}>
                            {col.type}
                          </span>
                        </td>
                        <td className="py-3 pl-4 text-xs dark:text-slate-400 text-slate-500">
                          {col.nullCount || 0}
                        </td>
                        <td className="py-3 pl-4 text-xs dark:text-slate-300 text-slate-600 truncate max-w-[200px]">
                          {col.sampleValues && Array.isArray(col.sampleValues)
                            ? col.sampleValues.join(', ')
                            : 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          ) : (
            <div className="glass-card p-6 h-full flex flex-col items-center justify-center min-h-[400px]">
              <Database className="w-12 h-12 text-slate-600 dark:text-slate-500 mb-3" />
              <h3 className="text-base font-bold dark:text-slate-200 text-slate-700">No Dataset Selected</h3>
              <p className="text-xs dark:text-slate-400 text-slate-500 text-center max-w-sm mt-1">
                Upload a CSV or Excel business data file on the left panel or select an existing dataset from your history to begin analyzing.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Datasets;
