import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { History, Filter, Search, Eye, Download, ChevronLeft, ChevronRight } from 'lucide-react';
import { Card, PageHeader, Button, Input, Select, RiskBadge, EmptyState, Skeleton, SectionHeader } from '@/components/ui';
import { predictionApi } from '@/api/predictionApi';
import { formatDateTime, getModelDisplayName, getRiskHex, formatPercentRaw, clsx } from '@/utils';

const PredictionHistory: React.FC = () => {
  const [predictions, setPredictions] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const [modelFilter, setModelFilter] = useState('');
  const pageSize = 10;

  useEffect(() => {
    setLoading(true);
    predictionApi.getHistory({ page, pageSize, risk: riskFilter || undefined, model: modelFilter || undefined })
      .then(res => {
        setPredictions(res.data);
        setTotal(res.total);
        setTotalPages(res.totalPages);
        setLoading(false);
      });
  }, [page, riskFilter, modelFilter]);

  const filtered = search
    ? predictions.filter(p => p.companyName.toLowerCase().includes(search.toLowerCase()))
    : predictions;

  const STATUS_CLS: Record<string, string> = {
    completed: 'badge-success',
    pending: 'badge-warning',
    failed: 'badge-danger',
  };

  return (
    <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <PageHeader
        title="Prediction History"
        subtitle={`${total} predictions recorded`}
        breadcrumb={['Prediction History']}
        actions={
          <Button variant="secondary" size="sm" leftIcon={<Download className="w-3.5 h-3.5" />}>Export CSV</Button>
        }
      />

      {/* Filters */}
      <Card>
        <div className="flex flex-wrap gap-3">
          <div className="flex-1 min-w-48">
            <Input
              placeholder="Search by company name..."
              leftIcon={<Search className="w-4 h-4" />}
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
          <Select
            options={[
              { value: '', label: 'All Risk Levels' },
              { value: 'LOW', label: 'Low Risk' },
              { value: 'MEDIUM', label: 'Medium Risk' },
              { value: 'HIGH', label: 'High Risk' },
            ]}
            value={riskFilter}
            onChange={e => { setRiskFilter(e.target.value); setPage(1); }}
            className="w-44"
          />
          <Select
            options={[
              { value: '', label: 'All Models' },
              { value: 'gnn', label: 'Graph Neural Network' },
              { value: 'xgboost', label: 'XGBoost' },
              { value: 'svm', label: 'SVM' },
              { value: 'logistic_regression', label: 'Logistic Regression' },
            ]}
            value={modelFilter}
            onChange={e => { setModelFilter(e.target.value); setPage(1); }}
            className="w-52"
          />
        </div>
      </Card>

      {/* Table */}
      <Card padding={false}>
        <div className="p-5 border-b border-surface-200">
          <SectionHeader
            title="All Predictions"
            subtitle={loading ? '...' : `${filtered.length} results`}
          />
        </div>
        {loading ? (
          <div className="p-5 space-y-3">
            {Array.from({ length: 8 }).map((_, i) => <Skeleton key={i} className="h-12" />)}
          </div>
        ) : filtered.length === 0 ? (
          <EmptyState
            icon={<History className="w-12 h-12" />}
            title="No predictions found"
            description="Run a risk assessment to see it appear here."
          />
        ) : (
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr>
                  <th>Date & Time</th>
                  <th>Company</th>
                  <th>Default Prob.</th>
                  <th>Risk Category</th>
                  <th>Model</th>
                  <th>Confidence</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((p) => (
                  <tr key={p.id}>
                    <td className="text-xs tabular-nums">{formatDateTime(p.date)}</td>
                    <td>
                      <div>
                        <p className="font-medium">{p.companyName}</p>
                        <p className="text-2xs text-content-tertiary">{p.id}</p>
                      </div>
                    </td>
                    <td>
                      <span className="text-sm font-semibold tabular-nums" style={{ color: getRiskHex(p.riskCategory) }}>
                        {formatPercentRaw(p.defaultProbability * 100)}
                      </span>
                    </td>
                    <td><RiskBadge risk={p.riskCategory} /></td>
                    <td><span className="text-xs text-content-secondary">{getModelDisplayName(p.modelUsed)}</span></td>
                    <td className="tabular-nums text-xs">{formatPercentRaw(p.confidence * 100)}</td>
                    <td>
                      <span className={clsx('badge', STATUS_CLS[p.status] || 'badge-neutral')}>
                        {p.status}
                      </span>
                    </td>
                    <td>
                      <Button variant="ghost" size="sm" leftIcon={<Eye className="w-3 h-3" />}>
                        View
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="p-4 border-t border-surface-200 flex items-center justify-between">
            <p className="text-xs text-content-secondary">Page {page} of {totalPages}</p>
            <div className="flex items-center gap-1">
              <button
                disabled={page <= 1}
                onClick={() => setPage(p => p - 1)}
                className="btn btn-secondary btn-sm btn-icon disabled:opacity-40"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
              </button>
              {Array.from({ length: Math.min(5, totalPages) }).map((_, i) => {
                const p = i + 1;
                return (
                  <button
                    key={p}
                    onClick={() => setPage(p)}
                    className={clsx(
                      'w-8 h-8 text-xs rounded-lg font-medium',
                      page === p ? 'bg-primary text-white' : 'text-content-secondary hover:bg-surface-100'
                    )}
                  >
                    {p}
                  </button>
                );
              })}
              <button
                disabled={page >= totalPages}
                onClick={() => setPage(p => p + 1)}
                className="btn btn-secondary btn-sm btn-icon disabled:opacity-40"
              >
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}
      </Card>
    </motion.div>
  );
};

export default PredictionHistory;
