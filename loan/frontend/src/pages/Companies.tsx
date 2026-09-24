import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search, Filter, Building2, Eye, TrendingUp, Download } from 'lucide-react';
import {
  Card, PageHeader, Button, Input, Select, RiskBadge, EmptyState, Skeleton, SectionHeader,
} from '@/components/ui';
import { companyApi } from '@/api/companyApi';
import type { Company } from '@/types';
import { formatCurrency, formatPercentRaw, getRiskHex, getNetworkExposureColor, clsx } from '@/utils';

const Companies: React.FC = () => {
  const navigate = useNavigate();
  const [companies, setCompanies] = useState<Company[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const pageSize = 10;

  const fetchCompanies = async () => {
    setLoading(true);
    try {
      const res = await companyApi.getAll({ page, pageSize, risk: riskFilter || undefined, search: search || undefined });
      setCompanies(res.data);
      setTotal(res.total);
      setTotalPages(res.totalPages);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchCompanies(); }, [page, riskFilter, search]);

  // Search with debounce
  useEffect(() => {
    const t = setTimeout(() => { setPage(1); fetchCompanies(); }, 400);
    return () => clearTimeout(t);
  }, [search]);

  return (
    <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <PageHeader
        title="Maritime Companies"
        subtitle={`${total.toLocaleString()} shipping companies monitored`}
        breadcrumb={['Companies']}
        actions={
          <div className="flex gap-2">
            <Button variant="secondary" size="sm" leftIcon={<Download className="w-3.5 h-3.5" />}>Export</Button>
            <Button size="sm" leftIcon={<Building2 className="w-3.5 h-3.5" />} onClick={() => navigate('/prediction')}>New Assessment</Button>
          </div>
        }
      />

      {/* Filters */}
      <Card>
        <div className="flex flex-wrap gap-3">
          <div className="flex-1 min-w-48">
            <Input
              placeholder="Search companies..."
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
          <Button variant="secondary" size="sm" leftIcon={<Filter className="w-3.5 h-3.5" />}>
            More Filters
          </Button>
        </div>
      </Card>

      {/* Table */}
      <Card padding={false}>
        <div className="p-5 border-b border-surface-200">
          <SectionHeader
            title="Company Risk Registry"
            subtitle={loading ? 'Loading...' : `Showing ${companies.length} of ${total} companies`}
          />
        </div>
        {loading ? (
          <div className="p-5 space-y-3">
            {Array.from({ length: 8 }).map((_, i) => <Skeleton key={i} className="h-12" />)}
          </div>
        ) : companies.length === 0 ? (
          <EmptyState
            icon={<Building2 className="w-12 h-12" />}
            title="No companies found"
            description="Try adjusting your search or filter criteria."
          />
        ) : (
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr>
                  <th>Company</th>
                  <th>Segment</th>
                  <th>Loan Amount</th>
                  <th>Vessel Value</th>
                  <th>Debt/Equity</th>
                  <th>Default Prob.</th>
                  <th>Risk</th>
                  <th>Network Risk</th>
                  <th>Fleet</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {companies.map(c => (
                  <tr key={c.id} className="cursor-pointer" onClick={() => navigate(`/companies/${c.id}`)}>
                    <td>
                      <div>
                        <p className="font-medium text-content-primary">{c.name}</p>
                        <p className="text-2xs text-content-tertiary">{c.id} · {c.country}</p>
                      </div>
                    </td>
                    <td><span className="badge-neutral badge">{c.segment}</span></td>
                    <td className="tabular-nums font-medium">{formatCurrency(c.loanAmount)}</td>
                    <td className="tabular-nums">{formatCurrency(c.vesselValue)}</td>
                    <td className="tabular-nums font-medium">{c.debtToEquity.toFixed(2)}x</td>
                    <td>
                      <div className="flex items-center gap-2">
                        <div className="w-12 bg-surface-100 rounded-full h-1.5">
                          <div
                            className="h-1.5 rounded-full"
                            style={{ width: `${c.defaultProbability * 100}%`, backgroundColor: getRiskHex(c.riskCategory) }}
                          />
                        </div>
                        <span className="text-xs font-semibold tabular-nums" style={{ color: getRiskHex(c.riskCategory) }}>
                          {formatPercentRaw(c.defaultProbability * 100)}
                        </span>
                      </div>
                    </td>
                    <td><RiskBadge risk={c.riskCategory} /></td>
                    <td><span className={clsx('text-xs font-medium', getNetworkExposureColor(c.networkRisk))}>{c.networkRisk}</span></td>
                    <td className="text-xs tabular-nums">{c.fleetSize} vessels</td>
                    <td onClick={e => e.stopPropagation()}>
                      <div className="flex gap-1">
                        <Button variant="ghost" size="sm" leftIcon={<Eye className="w-3 h-3" />}
                          onClick={() => navigate(`/companies/${c.id}`)}>
                          View
                        </Button>
                      </div>
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
            <p className="text-xs text-content-secondary">
              Page {page} of {totalPages} · {total} total
            </p>
            <div className="flex gap-1">
              <Button variant="secondary" size="sm" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>
                Previous
              </Button>
              {Array.from({ length: Math.min(5, totalPages) }).map((_, i) => {
                const p = i + 1;
                return (
                  <button
                    key={p}
                    onClick={() => setPage(p)}
                    className={clsx(
                      'w-8 h-8 text-xs rounded-lg font-medium transition-all',
                      page === p ? 'bg-primary text-white' : 'text-content-secondary hover:bg-surface-100'
                    )}
                  >
                    {p}
                  </button>
                );
              })}
              <Button variant="secondary" size="sm" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>
                Next
              </Button>
            </div>
          </div>
        )}
      </Card>
    </motion.div>
  );
};

export default Companies;
