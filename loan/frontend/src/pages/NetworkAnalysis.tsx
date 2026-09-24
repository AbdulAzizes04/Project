import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Network, Search, Filter, Info, ZoomIn, ZoomOut, RefreshCw } from 'lucide-react';
import { Card, PageHeader, Button, Input, Select, RiskBadge, SectionHeader } from '@/components/ui';
import { networkApi } from '@/api/networkApi';
import type { NetworkGraph, NetworkNode } from '@/types';
import { getRiskHex, formatPercent, clsx } from '@/utils';

// ============================================================
// SIMPLE SVG NETWORK GRAPH
// ============================================================
const NetworkGraphCanvas: React.FC<{
  graph: NetworkGraph;
  selectedNode: string | null;
  onSelect: (id: string | null) => void;
}> = ({ graph, selectedNode, onSelect }) => {
  const [tooltip, setTooltip] = useState<{ node: NetworkNode; x: number; y: number } | null>(null);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [dragging, setDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const svgRef = useRef<SVGSVGElement>(null);

  const nodeMap = new Map(graph.nodes.map(n => [n.id, n]));

  const getNodeColor = (node: NetworkNode) => {
    if (node.id === selectedNode) return '#F59E0B';
    return getRiskHex(node.riskCategory);
  };

  const getNodeRadius = (node: NetworkNode) => {
    const base = 8;
    return base + node.centrality * 12;
  };

  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    setZoom(z => Math.max(0.4, Math.min(2.5, z - e.deltaY * 0.001)));
  }, []);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    setDragging(true);
    setDragStart({ x: e.clientX - offset.x, y: e.clientY - offset.y });
  }, [offset]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (dragging) {
      setOffset({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
    }
  }, [dragging, dragStart]);

  const handleMouseUp = useCallback(() => setDragging(false), []);

  return (
    <div className="relative w-full h-full">
      <svg
        ref={svgRef}
        className="w-full h-full cursor-grab active:cursor-grabbing"
        style={{ background: '#FAFAFA' }}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <g transform={`translate(${offset.x},${offset.y}) scale(${zoom})`}>
          {/* Edges */}
          {graph.edges.map((edge, i) => {
            const src = nodeMap.get(edge.source);
            const tgt = nodeMap.get(edge.target);
            if (!src || !tgt || !src.x || !tgt.x) return null;
            const isHighlighted = selectedNode === edge.source || selectedNode === edge.target;
            return (
              <line
                key={i}
                x1={src.x} y1={src.y}
                x2={tgt.x} y2={tgt.y}
                stroke={isHighlighted ? '#F59E0B' : '#E5E7EB'}
                strokeWidth={isHighlighted ? 2 : 1}
                strokeOpacity={isHighlighted ? 0.8 : 0.5}
              />
            );
          })}

          {/* Nodes */}
          {graph.nodes.map(node => {
            if (!node.x || !node.y) return null;
            const isSelected = node.id === selectedNode;
            const color = getNodeColor(node);
            const r = getNodeRadius(node);
            return (
              <g key={node.id}
                onClick={() => onSelect(isSelected ? null : node.id)}
                onMouseEnter={e => setTooltip({ node, x: e.clientX, y: e.clientY })}
                onMouseLeave={() => setTooltip(null)}
                className="cursor-pointer"
              >
                {isSelected && (
                  <circle cx={node.x} cy={node.y} r={r + 6} fill={color} fillOpacity={0.15} />
                )}
                <circle
                  cx={node.x} cy={node.y} r={r}
                  fill={color}
                  stroke={isSelected ? '#F59E0B' : 'white'}
                  strokeWidth={isSelected ? 2.5 : 1.5}
                  fillOpacity={0.9}
                />
                <text
                  x={node.x} y={node.y + r + 12}
                  textAnchor="middle"
                  fontSize={9}
                  fill="#6B7280"
                >
                  {node.name.split(' ')[0]}
                </text>
              </g>
            );
          })}
        </g>
      </svg>

      {/* Tooltip */}
      {tooltip && (
        <div
          className="absolute z-10 bg-white border border-surface-200 rounded-xl shadow-dropdown p-3 pointer-events-none text-xs"
          style={{ left: tooltip.x + 12, top: tooltip.y - 40 }}
        >
          <p className="font-semibold text-content-primary">{tooltip.node.name}</p>
          <p className="text-content-secondary mt-0.5">
            Default: {(tooltip.node.defaultProbability * 100).toFixed(1)}%
          </p>
          <p className="text-content-secondary">Centrality: {tooltip.node.centrality.toFixed(3)}</p>
        </div>
      )}

      {/* Zoom controls */}
      <div className="absolute top-3 right-3 flex flex-col gap-1">
        <button onClick={() => setZoom(z => Math.min(2.5, z + 0.15))}
          className="w-7 h-7 bg-white border border-surface-200 rounded-lg flex items-center justify-center hover:bg-surface-50 shadow-card">
          <ZoomIn className="w-3.5 h-3.5 text-content-secondary" />
        </button>
        <button onClick={() => setZoom(z => Math.max(0.4, z - 0.15))}
          className="w-7 h-7 bg-white border border-surface-200 rounded-lg flex items-center justify-center hover:bg-surface-50 shadow-card">
          <ZoomOut className="w-3.5 h-3.5 text-content-secondary" />
        </button>
        <button onClick={() => { setZoom(1); setOffset({ x: 0, y: 0 }); }}
          className="w-7 h-7 bg-white border border-surface-200 rounded-lg flex items-center justify-center hover:bg-surface-50 shadow-card">
          <RefreshCw className="w-3.5 h-3.5 text-content-secondary" />
        </button>
      </div>

      {/* Legend */}
      <div className="absolute bottom-3 left-3 bg-white border border-surface-200 rounded-xl p-3 shadow-card">
        <p className="text-2xs font-semibold text-content-secondary mb-2 uppercase tracking-wider">Legend</p>
        {[
          { color: '#16A34A', label: 'Low Risk' },
          { color: '#F59E0B', label: 'Selected / Medium' },
          { color: '#DC2626', label: 'High Risk' },
        ].map(l => (
          <div key={l.label} className="flex items-center gap-2 mb-1 last:mb-0">
            <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: l.color }} />
            <span className="text-2xs text-content-secondary">{l.label}</span>
          </div>
        ))}
        <p className="text-2xs text-content-tertiary mt-2">Node size = centrality</p>
      </div>
    </div>
  );
};

// ============================================================
// MAIN PAGE
// ============================================================
const NetworkAnalysis: React.FC = () => {
  const [graph, setGraph] = useState<NetworkGraph | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [riskFilter, setRiskFilter] = useState('');

  useEffect(() => {
    networkApi.getGraph().then(g => {
      setGraph(g);
      setLoading(false);
    });
  }, []);

  const selectedNode = graph?.nodes.find(n => n.id === selectedId);
  const filteredGraph = graph && riskFilter
    ? { ...graph, nodes: graph.nodes.filter(n => n.riskCategory === riskFilter) }
    : graph;

  return (
    <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <PageHeader
        title="Maritime Financial Network"
        subtitle="Interactive visualization of financial relationships and risk propagation pathways"
        breadcrumb={['Network Analysis']}
        actions={
          <div className="flex gap-2">
            <Select
              options={[
                { value: '', label: 'All Risk Levels' },
                { value: 'LOW', label: 'Low Risk' },
                { value: 'MEDIUM', label: 'Medium Risk' },
                { value: 'HIGH', label: 'High Risk' },
              ]}
              value={riskFilter}
              onChange={e => setRiskFilter(e.target.value)}
              className="w-40"
            />
          </div>
        }
      />

      {/* Stats row */}
      {graph && (
        <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
          {[
            { label: 'Companies', value: graph.metadata.totalNodes },
            { label: 'Connections', value: graph.metadata.totalEdges },
            { label: 'Avg Centrality', value: graph.metadata.avgCentrality.toFixed(3) },
            { label: 'Network Density', value: graph.metadata.density.toFixed(3) },
          ].map(m => (
            <Card key={m.label}>
              <p className="stat-label">{m.label}</p>
              <p className="stat-value mt-1 tabular-nums">{m.value}</p>
            </Card>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-4">
        {/* Graph */}
        <div className="xl:col-span-3">
          <Card padding={false} className="overflow-hidden" style={{ height: 560 }}>
            {loading ? (
              <div className="flex items-center justify-center h-full text-content-tertiary">
                <div className="text-center">
                  <Network className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">Loading network...</p>
                </div>
              </div>
            ) : filteredGraph ? (
              <NetworkGraphCanvas
                graph={filteredGraph}
                selectedNode={selectedId}
                onSelect={setSelectedId}
              />
            ) : null}
          </Card>
        </div>

        {/* Side Panel */}
        <div className="space-y-4">
          {selectedNode ? (
            <Card>
              <SectionHeader title="Selected Company" />
              <div className="space-y-3">
                <div>
                  <p className="text-sm font-semibold text-content-primary">{selectedNode.name}</p>
                  <div className="mt-1"><RiskBadge risk={selectedNode.riskCategory} /></div>
                </div>
                <div className="divider" />
                {[
                  { label: 'Default Probability', value: `${(selectedNode.defaultProbability * 100).toFixed(1)}%` },
                  { label: 'Centrality Score', value: selectedNode.centrality.toFixed(3) },
                  { label: 'Degree', value: selectedNode.degree },
                ].map(m => (
                  <div key={m.label} className="flex justify-between">
                    <span className="text-xs text-content-secondary">{m.label}</span>
                    <span className="text-xs font-semibold text-content-primary">{m.value}</span>
                  </div>
                ))}
                <button onClick={() => setSelectedId(null)} className="w-full btn btn-secondary btn-sm mt-2">
                  Deselect
                </button>
              </div>
            </Card>
          ) : (
            <Card>
              <div className="empty-state py-6">
                <Info className="w-8 h-8 text-content-tertiary" />
                <p className="empty-state-title text-sm">Click a node</p>
                <p className="empty-state-desc text-xs">Select a company node to view its network details</p>
              </div>
            </Card>
          )}

          {/* Node list */}
          <Card>
            <SectionHeader title="Highest Risk Nodes" />
            <div className="space-y-2">
              {(filteredGraph?.nodes || [])
                .sort((a, b) => b.defaultProbability - a.defaultProbability)
                .slice(0, 6)
                .map(n => (
                  <button
                    key={n.id}
                    onClick={() => setSelectedId(n.id)}
                    className={clsx(
                      'w-full flex items-center justify-between p-2 rounded-lg text-left hover:bg-surface-50 transition-colors',
                      selectedId === n.id && 'bg-primary-light'
                    )}
                  >
                    <div>
                      <p className="text-xs font-medium text-content-primary truncate max-w-32">{n.name.split(' ')[0]}</p>
                      <RiskBadge risk={n.riskCategory} className="mt-0.5" />
                    </div>
                    <span className="text-xs font-semibold" style={{ color: getRiskHex(n.riskCategory) }}>
                      {(n.defaultProbability * 100).toFixed(0)}%
                    </span>
                  </button>
                ))}
            </div>
          </Card>
        </div>
      </div>
    </motion.div>
  );
};

export default NetworkAnalysis;
