import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Upload, FileText, CheckCircle, AlertCircle, Database, X, Eye, Play, RefreshCw, Download, FileSpreadsheet, Info } from 'lucide-react';
import { Card, PageHeader, Button, SectionHeader, ProgressBar, Spinner } from '@/components/ui';
import { mockDatasets } from '@/services/mock/mockData';
import type { DatasetInfo } from '@/types';
import { formatDate, clsx } from '@/utils';

const STATUS_CONFIG = {
  uploaded:    { label: 'Uploaded',    color: 'badge-neutral', icon: <FileText className="w-3 h-3" /> },
  validating:  { label: 'Validating',  color: 'badge-info',    icon: <RefreshCw className="w-3 h-3 animate-spin" /> },
  cleaning:    { label: 'Cleaning',    color: 'badge-warning', icon: <RefreshCw className="w-3 h-3 animate-spin" /> },
  processing:  { label: 'Processing',  color: 'badge-warning', icon: <RefreshCw className="w-3 h-3 animate-spin" /> },
  ready:       { label: 'Ready',       color: 'badge-success', icon: <CheckCircle className="w-3 h-3" /> },
  error:       { label: 'Error',       color: 'badge-danger',  icon: <AlertCircle className="w-3 h-3" /> },
};

const SAMPLE_CSV_CONTENT = `company_id,company_name,vessel_type,fleet_size,avg_vessel_age,annual_revenue,total_debt,debt_to_equity,interest_coverage_ratio,cash_and_equivalents,loan_amount,loan_term_months,interest_rate,collateral_value,loan_to_value,bdi_index,fuel_oil_price,network_centrality,betti_0,betti_1,persistence_entropy,default
COMP-001,Norden Maritime Corp,Bulker,18,8.2,48500000,28000000,1.45,3.20,6200000,25000000,60,6.50,38000000,0.66,1820,540,0.64,12,3,1.42,0
COMP-002,Aegean Bulk Shipping,Bulker,6,16.4,14200000,22000000,2.90,1.15,1100000,18500000,48,8.25,19000000,0.97,1450,580,0.82,8,6,2.15,1
COMP-003,Starlight Tankers Ltd,Tanker,22,6.0,72000000,35000000,1.10,4.10,14500000,42000000,72,5.75,65000000,0.65,2100,510,0.45,15,2,1.18,0
COMP-004,Levant Cargo Lines,Container,4,19.2,9800000,16500000,3.40,0.95,850000,12000000,36,7.80,12500000,0.96,1300,610,0.78,6,5,2.34,1
COMP-005,Nordic Feeder Alliance,Container,11,9.5,31000000,19000000,1.75,2.60,4200000,24000000,60,6.10,32000000,0.75,1750,535,0.52,10,2,1.31,0
COMP-006,Hellas Gas Carriers,LNG Carrier,8,4.2,56000000,38000000,1.35,3.80,9500000,35000000,84,5.90,52000000,0.67,1950,520,0.38,14,1,0.95,0
COMP-007,Black Sea Dry Bulk,Bulker,5,17.8,8500000,15000000,3.10,0.88,600000,10500000,36,8.50,11000000,0.95,1280,620,0.85,5,7,2.58,1
COMP-008,Caspian Energy Logistics,Tanker,14,11.0,38000000,24000000,1.80,2.40,3800000,20000000,60,6.85,28000000,0.71,1680,560,0.61,11,3,1.60,0
COMP-009,Pacific Navigator Line,Container,16,7.4,52000000,30000000,1.50,3.10,7800000,28000000,60,6.30,40000000,0.70,1810,550,0.58,13,2,1.38,0
COMP-010,Viking Offshore Tankers,Tanker,9,13.2,26000000,21000000,2.40,1.65,2100000,16000000,48,7.40,20500000,0.78,1590,575,0.70,9,4,1.82,0`;

const DataManagement: React.FC = () => {
  const [datasets, setDatasets] = useState<DatasetInfo[]>(mockDatasets);
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [selectedDs, setSelectedDs] = useState<DatasetInfo | null>(mockDatasets[0] || null);

  const downloadSampleCSV = () => {
    const blob = new Blob([SAMPLE_CSV_CONTENT], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'maritime_loan_sample_template.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith('.csv')) simulateUpload(file.name, file);
  }, [datasets.length]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) simulateUpload(file.name, file);
  };

  const simulateUpload = async (filename: string, file?: File) => {
    setUploading(true);
    setProgress(0);
    const id = `DS-${String(datasets.length + 1).padStart(3, '0')}`;
    const newDs: DatasetInfo = {
      id, filename,
      rows: 0, columns: 0, missingValues: 0,
      numericalFeatures: 0, categoricalFeatures: 0,
      uploadedAt: new Date().toISOString(),
      status: 'uploaded',
    };
    setDatasets(ds => [newDs, ...ds]);
    setSelectedDs(newDs);

    // Parse file if provided
    let parsedRows = 0;
    let parsedCols = 0;
    let parsedPreview: Record<string, any>[] | undefined;
    let numFeatures = 0;
    let catFeatures = 0;

    if (file) {
      try {
        const text = await file.text();
        const lines = text.trim().split('\n').filter(l => l.trim().length > 0);
        if (lines.length > 1) {
          const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
          parsedCols = headers.length;
          parsedRows = lines.length - 1;
          
          parsedPreview = lines.slice(1, 6).map(line => {
            const vals = line.split(',').map(v => v.trim().replace(/^"|"$/g, ''));
            const row: Record<string, any> = {};
            headers.forEach((h, idx) => {
              const val = vals[idx] ?? '';
              row[h] = !isNaN(Number(val)) && val !== '' ? Number(val) : val;
            });
            return row;
          });

          // Check feature types from first row
          if (parsedPreview[0]) {
            Object.values(parsedPreview[0]).forEach(val => {
              if (typeof val === 'number') numFeatures++;
              else catFeatures++;
            });
          }
        }
      } catch (err) {
        console.warn('Could not parse uploaded CSV text directly', err);
      }
    }

    let prog = 0;
    const stages: DatasetInfo['status'][] = ['validating', 'cleaning', 'processing', 'ready'];
    let stageIdx = 0;

    const timer = setInterval(() => {
      prog += Math.random() * 15;
      setProgress(Math.min(prog, 100));
      if (prog > (stageIdx + 1) * 25) {
        const status = stages[Math.min(stageIdx, stages.length - 1)];
        setDatasets(ds => ds.map(d => d.id === id ? { ...d, status } : d));
        setSelectedDs(d => d?.id === id ? { ...d!, status } : d);
        stageIdx++;
      }
      if (prog >= 100) {
        clearInterval(timer);
        setUploading(false);
        const finalDs: DatasetInfo = {
          ...newDs,
          status: 'ready',
          rows: parsedRows || Math.floor(Math.random() * 2000) + 500,
          columns: parsedCols || Math.floor(Math.random() * 30) + 20,
          missingValues: Math.floor(Math.random() * 20),
          numericalFeatures: numFeatures || Math.floor(Math.random() * 25) + 10,
          categoricalFeatures: catFeatures || Math.floor(Math.random() * 8) + 2,
          preview: parsedPreview || Array.from({ length: 5 }).map((_, i) => ({
            company_id: `COMP-${String(i + 1).padStart(4, '0')}`,
            loan_amount: (i + 1) * 12_500_000,
            vessel_age: 5 + i * 2,
            default: i === 0 ? 1 : 0,
          })),
        };
        setDatasets(ds => ds.map(d => d.id === id ? finalDs : d));
        setSelectedDs(finalDs);
      }
    }, 200);
  };

  return (
    <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <PageHeader
        title="Data Management"
        subtitle="Upload, validate, and process maritime loan datasets for model training and analysis"
        breadcrumb={['Data Management']}
        actions={
          <Button
            variant="secondary"
            leftIcon={<Download className="w-4 h-4 text-primary" />}
            onClick={downloadSampleCSV}
          >
            Download Sample CSV Template
          </Button>
        }
      />

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        {/* Upload + Dataset list */}
        <div className="space-y-4">
          {/* Upload Zone */}
          <Card>
            <div className="flex items-center justify-between mb-4">
              <SectionHeader title="Upload Dataset" subtitle="Supported: CSV files" />
              <button
                type="button"
                onClick={downloadSampleCSV}
                className="text-xs text-primary font-medium hover:underline inline-flex items-center gap-1"
                title="Download standard template with 22 maritime financial & TDA features"
              >
                <Download className="w-3.5 h-3.5" />
                Template
              </button>
            </div>
            <label
              className={clsx(
                'block border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all',
                isDragOver ? 'border-primary bg-primary-light' : 'border-surface-200 hover:border-primary/50 hover:bg-surface-50'
              )}
              onDragOver={e => { e.preventDefault(); setIsDragOver(true); }}
              onDragLeave={() => setIsDragOver(false)}
              onDrop={handleDrop}
            >
              <input type="file" accept=".csv" className="hidden" onChange={handleFileChange} />
              <Upload className={clsx('w-8 h-8 mx-auto mb-2', isDragOver ? 'text-primary' : 'text-content-tertiary')} />
              <p className="text-sm font-medium text-content-primary">Drop CSV file here</p>
              <p className="text-xs text-content-tertiary mt-1">or click to browse from device</p>
            </label>

            {/* Quick Template Callout */}
            <div className="mt-3 p-3 bg-surface-50 rounded-xl border border-surface-200 flex items-start gap-2.5">
              <FileSpreadsheet className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
              <div className="flex-1 text-xs">
                <p className="font-semibold text-content-primary">Need test data?</p>
                <p className="text-content-secondary mt-0.5">
                  Download the sample template pre-configured with 22 financial, fleet, market, and TDA columns.
                </p>
                <button
                  type="button"
                  onClick={downloadSampleCSV}
                  className="mt-2 text-xs font-semibold text-primary hover:text-primary-dark inline-flex items-center gap-1"
                >
                  <Download className="w-3 h-3" />
                  Download sample_template.csv
                </button>
              </div>
            </div>

            {uploading && (
              <div className="mt-3 space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-content-secondary">Processing...</span>
                  <span className="text-primary font-semibold">{Math.round(progress)}%</span>
                </div>
                <ProgressBar value={Math.round(progress)} color="#F59E0B" />
              </div>
            )}
          </Card>

          {/* Dataset List */}
          <Card>
            <SectionHeader title="Datasets" subtitle={`${datasets.length} files`} />
            <div className="space-y-2">
              {datasets.map(ds => {
                const sc = STATUS_CONFIG[ds.status];
                return (
                  <button
                    key={ds.id}
                    onClick={() => setSelectedDs(ds)}
                    className={clsx(
                      'w-full flex items-start gap-3 p-3 rounded-xl text-left transition-all',
                      selectedDs?.id === ds.id ? 'bg-primary-light border border-primary/20' : 'hover:bg-surface-50 border border-transparent'
                    )}
                  >
                    <FileText className="w-4 h-4 text-content-tertiary flex-shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-content-primary truncate">{ds.filename}</p>
                      <div className="flex items-center gap-1.5 mt-1">
                        <span className={clsx('badge text-2xs', sc.color)}>
                          {sc.icon} {sc.label}
                        </span>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </Card>
        </div>

        {/* Dataset Details */}
        <div className="xl:col-span-2 space-y-4">
          {selectedDs ? (
            <>
              <Card>
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-sm font-bold text-content-primary">{selectedDs.filename}</h3>
                    <p className="text-xs text-content-secondary mt-0.5">{selectedDs.id} · {formatDate(selectedDs.uploadedAt)}</p>
                  </div>
                  <div className="flex gap-2">
                    <span className={clsx('badge', STATUS_CONFIG[selectedDs.status].color)}>
                      {STATUS_CONFIG[selectedDs.status].icon} {STATUS_CONFIG[selectedDs.status].label}
                    </span>
                  </div>
                </div>

                {selectedDs.status === 'ready' && (
                  <div className="grid grid-cols-2 xl:grid-cols-3 gap-3 mb-4">
                    {[
                      { label: 'Total Rows', value: selectedDs.rows.toLocaleString(), icon: <Database className="w-4 h-4" /> },
                      { label: 'Columns', value: selectedDs.columns, icon: <FileText className="w-4 h-4" /> },
                      { label: 'Missing Values', value: selectedDs.missingValues, icon: <AlertCircle className="w-4 h-4" /> },
                      { label: 'Numerical Features', value: selectedDs.numericalFeatures, icon: <CheckCircle className="w-4 h-4" /> },
                      { label: 'Categorical Features', value: selectedDs.categoricalFeatures, icon: <CheckCircle className="w-4 h-4" /> },
                      { label: 'Data Quality', value: `${(100 - (selectedDs.missingValues / (selectedDs.rows * selectedDs.columns)) * 100).toFixed(1)}%`, icon: <CheckCircle className="w-4 h-4" /> },
                    ].map(m => (
                      <div key={m.label} className="bg-surface-50 rounded-xl p-3 border border-surface-200">
                        <div className="flex items-center gap-1.5 mb-1 text-content-tertiary">{m.icon}
                          <p className="text-2xs uppercase tracking-wider">{m.label}</p>
                        </div>
                        <p className="text-lg font-bold text-content-primary tabular-nums">{m.value}</p>
                      </div>
                    ))}
                  </div>
                )}

                {selectedDs.status === 'ready' && (
                  <div className="flex gap-2 flex-wrap">
                    <Button size="sm" leftIcon={<Eye className="w-3.5 h-3.5" />} variant="secondary">Preview Data</Button>
                    <Button size="sm" leftIcon={<CheckCircle className="w-3.5 h-3.5" />} variant="secondary">Validate</Button>
                    <Button size="sm" leftIcon={<RefreshCw className="w-3.5 h-3.5" />} variant="secondary">Clean</Button>
                    <Button size="sm" leftIcon={<Play className="w-3.5 h-3.5" />}>Run Analysis</Button>
                  </div>
                )}
              </Card>

              {/* Preview Table */}
              {selectedDs.preview && selectedDs.status === 'ready' && (
                <Card padding={false}>
                  <div className="p-4 border-b border-surface-200">
                    <SectionHeader title="Dataset Preview" subtitle="First 5 rows" />
                  </div>
                  <div className="table-wrapper">
                    <table className="table">
                      <thead>
                        <tr>
                          {Object.keys(selectedDs.preview[0] || {}).map(col => (
                            <th key={col}>{col}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {selectedDs.preview.map((row, i) => (
                          <tr key={i}>
                            {Object.values(row).map((val, j) => (
                              <td key={j} className="tabular-nums">
                                {typeof val === 'number' ? val.toLocaleString() : String(val)}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </Card>
              )}
            </>
          ) : (
            <Card>
              <div className="empty-state py-16">
                <Database className="w-12 h-12 text-content-tertiary" />
                <p className="empty-state-title">No dataset selected</p>
                <p className="empty-state-desc">Upload a CSV file or select an existing dataset</p>
              </div>
            </Card>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default DataManagement;
